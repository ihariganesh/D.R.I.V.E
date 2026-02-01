"""
Server Aggregator - Surveillance Network Core B
Central server that receives events from camera clients

Features:
- Receives event alerts from multiple cameras
- Stores events in SQLite database
- Provides REST API for event querying
- Natural language event search
"""

import os
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict

from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# Database path
DB_PATH = os.path.join(os.path.dirname(__file__), 'events.db')


def get_db_connection():
    """Get database connection with row factory"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_database():
    """Initialize the SQLite database"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Events table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event_type TEXT NOT NULL,
            confidence REAL,
            timestamp TEXT NOT NULL,
            camera_id TEXT NOT NULL,
            location TEXT,
            bounding_box TEXT,
            description TEXT,
            frame_number INTEGER,
            severity TEXT DEFAULT 'low',
            acknowledged INTEGER DEFAULT 0,
            acknowledged_by TEXT,
            acknowledged_at TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Cameras table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS cameras (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            camera_id TEXT UNIQUE NOT NULL,
            location TEXT,
            status TEXT DEFAULT 'offline',
            capabilities TEXT,
            registered_at TEXT,
            last_seen_at TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Event search history
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS search_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            query TEXT NOT NULL,
            results_count INTEGER,
            searched_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create indexes
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_events_type ON events(event_type)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_events_camera ON events(camera_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_events_timestamp ON events(timestamp)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_events_severity ON events(severity)')
    
    conn.commit()
    conn.close()
    
    logger.info(f"Database initialized at {DB_PATH}")


def create_app():
    """Create Flask application"""
    app = Flask(__name__)
    CORS(app)
    
    # Initialize database
    init_database()
    
    # ========== Event Endpoints ==========
    
    @app.route('/api/events', methods=['POST'])
    def receive_event():
        """Receive event from camera client"""
        try:
            data = request.get_json()
            
            if not data:
                return jsonify({'error': 'No data provided'}), 400
            
            # Validate required fields
            required = ['event_type', 'timestamp', 'camera_id']
            for field in required:
                if field not in data:
                    return jsonify({'error': f'Missing field: {field}'}), 400
            
            # Store in database
            conn = get_db_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO events 
                (event_type, confidence, timestamp, camera_id, location, 
                 bounding_box, description, frame_number, severity)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                data['event_type'],
                data.get('confidence', 0.0),
                data['timestamp'],
                data['camera_id'],
                data.get('location'),
                json.dumps(data.get('bounding_box')) if data.get('bounding_box') else None,
                data.get('description'),
                data.get('frame_number', 0),
                data.get('severity', 'low')
            ))
            
            event_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            logger.info(f"Event stored: {data['event_type']} from {data['camera_id']} (ID: {event_id})")
            
            return jsonify({
                'success': True,
                'event_id': event_id,
                'message': 'Event stored successfully'
            })
            
        except Exception as e:
            logger.error(f"Error storing event: {e}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/events', methods=['GET'])
    def list_events():
        """List events with optional filters"""
        try:
            # Get query parameters
            event_type = request.args.get('event_type')
            camera_id = request.args.get('camera_id')
            severity = request.args.get('severity')
            start_time = request.args.get('start_time')
            end_time = request.args.get('end_time')
            limit = request.args.get('limit', 100, type=int)
            offset = request.args.get('offset', 0, type=int)
            
            # Build query
            query = 'SELECT * FROM events WHERE 1=1'
            params = []
            
            if event_type:
                query += ' AND event_type = ?'
                params.append(event_type)
            
            if camera_id:
                query += ' AND camera_id = ?'
                params.append(camera_id)
            
            if severity:
                query += ' AND severity = ?'
                params.append(severity)
            
            if start_time:
                query += ' AND timestamp >= ?'
                params.append(start_time)
            
            if end_time:
                query += ' AND timestamp <= ?'
                params.append(end_time)
            
            query += ' ORDER BY timestamp DESC LIMIT ? OFFSET ?'
            params.extend([limit, offset])
            
            # Execute query
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute(query, params)
            
            events = []
            for row in cursor.fetchall():
                event = dict(row)
                if event.get('bounding_box'):
                    event['bounding_box'] = json.loads(event['bounding_box'])
                events.append(event)
            
            # Get total count
            count_query = 'SELECT COUNT(*) FROM events WHERE 1=1'
            if event_type:
                count_query += f" AND event_type = '{event_type}'"
            
            cursor.execute(count_query)
            total = cursor.fetchone()[0]
            
            conn.close()
            
            return jsonify({
                'events': events,
                'total': total,
                'limit': limit,
                'offset': offset
            })
            
        except Exception as e:
            logger.error(f"Error listing events: {e}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/events/<int:event_id>', methods=['GET'])
    def get_event(event_id):
        """Get single event by ID"""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM events WHERE id = ?', (event_id,))
            row = cursor.fetchone()
            conn.close()
            
            if not row:
                return jsonify({'error': 'Event not found'}), 404
            
            event = dict(row)
            if event.get('bounding_box'):
                event['bounding_box'] = json.loads(event['bounding_box'])
            
            return jsonify(event)
            
        except Exception as e:
            logger.error(f"Error getting event: {e}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/events/<int:event_id>/acknowledge', methods=['POST'])
    def acknowledge_event(event_id):
        """Mark event as acknowledged"""
        try:
            data = request.get_json() or {}
            user = data.get('user', 'system')
            
            conn = get_db_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE events 
                SET acknowledged = 1, acknowledged_by = ?, acknowledged_at = ?
                WHERE id = ?
            ''', (user, datetime.now().isoformat(), event_id))
            
            if cursor.rowcount == 0:
                conn.close()
                return jsonify({'error': 'Event not found'}), 404
            
            conn.commit()
            conn.close()
            
            return jsonify({
                'success': True,
                'message': 'Event acknowledged'
            })
            
        except Exception as e:
            logger.error(f"Error acknowledging event: {e}")
            return jsonify({'error': str(e)}), 500
    
    # ========== Natural Language Search ==========
    
    @app.route('/api/events/search', methods=['GET', 'POST'])
    def search_events():
        """
        Natural language search for events
        
        Examples:
        - "person" -> Find all person detections
        - "fire in last hour" -> Fire events in last hour
        - "running person camera 1" -> Running person events from camera 1
        - "accident yesterday" -> Accident events from yesterday
        """
        try:
            if request.method == 'POST':
                data = request.get_json() or {}
                query = data.get('query', '')
            else:
                query = request.args.get('q', '')
            
            if not query:
                return jsonify({'error': 'No search query provided'}), 400
            
            # Parse natural language query
            search_params = _parse_search_query(query)
            
            # Build SQL query
            sql = 'SELECT * FROM events WHERE 1=1'
            params = []
            
            # Event type filter
            if search_params.get('event_types'):
                placeholders = ','.join(['?' for _ in search_params['event_types']])
                sql += f' AND event_type IN ({placeholders})'
                params.extend(search_params['event_types'])
            
            # Camera filter
            if search_params.get('camera_ids'):
                placeholders = ','.join(['?' for _ in search_params['camera_ids']])
                sql += f' AND camera_id IN ({placeholders})'
                params.extend(search_params['camera_ids'])
            
            # Time filter
            if search_params.get('start_time'):
                sql += ' AND timestamp >= ?'
                params.append(search_params['start_time'].isoformat())
            
            if search_params.get('end_time'):
                sql += ' AND timestamp <= ?'
                params.append(search_params['end_time'].isoformat())
            
            # Severity filter
            if search_params.get('severity'):
                sql += ' AND severity = ?'
                params.append(search_params['severity'])
            
            # Text search in description
            if search_params.get('text_search'):
                sql += ' AND description LIKE ?'
                params.append(f'%{search_params["text_search"]}%')
            
            sql += ' ORDER BY timestamp DESC LIMIT 100'
            
            # Execute search
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute(sql, params)
            
            events = []
            for row in cursor.fetchall():
                event = dict(row)
                if event.get('bounding_box'):
                    event['bounding_box'] = json.loads(event['bounding_box'])
                events.append(event)
            
            # Log search
            cursor.execute(
                'INSERT INTO search_history (query, results_count) VALUES (?, ?)',
                (query, len(events))
            )
            conn.commit()
            conn.close()
            
            return jsonify({
                'query': query,
                'parsed': search_params,
                'results': events,
                'count': len(events)
            })
            
        except Exception as e:
            logger.error(f"Error searching events: {e}")
            return jsonify({'error': str(e)}), 500
    
    def _parse_search_query(query: str) -> Dict:
        """
        Parse natural language search query
        
        Args:
            query: Natural language query string
            
        Returns:
            Dictionary of search parameters
        """
        query_lower = query.lower()
        params = {
            'event_types': [],
            'camera_ids': [],
            'start_time': None,
            'end_time': None,
            'severity': None,
            'text_search': None
        }
        
        # Event types
        event_keywords = {
            'person': 'person',
            'people': 'person',
            'human': 'person',
            'car': 'car',
            'vehicle': 'car',
            'truck': 'truck',
            'bus': 'bus',
            'motorcycle': 'motorcycle',
            'bike': 'bicycle',
            'bicycle': 'bicycle',
            'fire': 'fire',
            'flame': 'fire',
            'running': 'person_running',
            'run': 'person_running',
            'accident': 'accident',
            'crash': 'accident',
            'theft': 'theft',
            'steal': 'theft'
        }
        
        for keyword, event_type in event_keywords.items():
            if keyword in query_lower and event_type not in params['event_types']:
                params['event_types'].append(event_type)
        
        # Camera IDs
        import re
        camera_patterns = [
            r'camera\s*(\d+)',
            r'cam\s*(\d+)',
            r'cam(\d+)',
            r'camera\s*id\s*(\d+)'
        ]
        
        for pattern in camera_patterns:
            matches = re.findall(pattern, query_lower)
            for match in matches:
                cam_id = f'CAM{match.zfill(3)}'
                if cam_id not in params['camera_ids']:
                    params['camera_ids'].append(cam_id)
        
        # Time filters
        now = datetime.now()
        
        if 'last hour' in query_lower or 'past hour' in query_lower:
            params['start_time'] = now - timedelta(hours=1)
        elif 'last 24 hours' in query_lower or 'today' in query_lower:
            params['start_time'] = now - timedelta(hours=24)
        elif 'yesterday' in query_lower:
            params['start_time'] = now - timedelta(days=2)
            params['end_time'] = now - timedelta(days=1)
        elif 'last week' in query_lower:
            params['start_time'] = now - timedelta(weeks=1)
        elif 'last month' in query_lower:
            params['start_time'] = now - timedelta(days=30)
        
        # Time of day
        if 'morning' in query_lower:
            params['text_search'] = 'morning'
        elif 'evening' in query_lower:
            params['text_search'] = 'evening'
        elif 'night' in query_lower:
            params['text_search'] = 'night'
        
        # Severity
        if 'critical' in query_lower or 'urgent' in query_lower or 'emergency' in query_lower:
            params['severity'] = 'critical'
        elif 'high' in query_lower or 'important' in query_lower:
            params['severity'] = 'high'
        elif 'medium' in query_lower:
            params['severity'] = 'medium'
        
        return params
    
    # ========== Camera Endpoints ==========
    
    @app.route('/api/cameras/register', methods=['POST'])
    def register_camera():
        """Register a camera client"""
        try:
            data = request.get_json()
            
            if not data or 'camera_id' not in data:
                return jsonify({'error': 'camera_id required'}), 400
            
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # Upsert camera
            cursor.execute('''
                INSERT INTO cameras (camera_id, location, status, capabilities, registered_at, last_seen_at)
                VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT(camera_id) DO UPDATE SET
                    status = excluded.status,
                    location = excluded.location,
                    last_seen_at = excluded.last_seen_at
            ''', (
                data['camera_id'],
                data.get('location', 'Unknown'),
                'online',
                json.dumps(data.get('capabilities', [])),
                data.get('registered_at', datetime.now().isoformat()),
                datetime.now().isoformat()
            ))
            
            conn.commit()
            conn.close()
            
            logger.info(f"Camera registered: {data['camera_id']}")
            
            return jsonify({
                'success': True,
                'message': f"Camera {data['camera_id']} registered"
            })
            
        except Exception as e:
            logger.error(f"Error registering camera: {e}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/cameras/deregister', methods=['POST'])
    def deregister_camera():
        """Deregister a camera client"""
        try:
            data = request.get_json()
            
            if not data or 'camera_id' not in data:
                return jsonify({'error': 'camera_id required'}), 400
            
            conn = get_db_connection()
            cursor = conn.cursor()
            
            cursor.execute(
                'UPDATE cameras SET status = ? WHERE camera_id = ?',
                ('offline', data['camera_id'])
            )
            
            conn.commit()
            conn.close()
            
            logger.info(f"Camera deregistered: {data['camera_id']}")
            
            return jsonify({
                'success': True,
                'message': f"Camera {data['camera_id']} deregistered"
            })
            
        except Exception as e:
            logger.error(f"Error deregistering camera: {e}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/cameras', methods=['GET'])
    def list_cameras():
        """List all registered cameras"""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM cameras ORDER BY camera_id')
            
            cameras = []
            for row in cursor.fetchall():
                camera = dict(row)
                if camera.get('capabilities'):
                    camera['capabilities'] = json.loads(camera['capabilities'])
                cameras.append(camera)
            
            conn.close()
            
            return jsonify({
                'cameras': cameras,
                'total': len(cameras),
                'online': sum(1 for c in cameras if c['status'] == 'online')
            })
            
        except Exception as e:
            logger.error(f"Error listing cameras: {e}")
            return jsonify({'error': str(e)}), 500
    
    # ========== Statistics Endpoints ==========
    
    @app.route('/api/stats', methods=['GET'])
    def get_stats():
        """Get surveillance statistics"""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # Total events
            cursor.execute('SELECT COUNT(*) FROM events')
            total_events = cursor.fetchone()[0]
            
            # Events by type
            cursor.execute('''
                SELECT event_type, COUNT(*) as count 
                FROM events 
                GROUP BY event_type 
                ORDER BY count DESC
            ''')
            events_by_type = {row[0]: row[1] for row in cursor.fetchall()}
            
            # Events by severity
            cursor.execute('''
                SELECT severity, COUNT(*) as count 
                FROM events 
                GROUP BY severity
            ''')
            events_by_severity = {row[0]: row[1] for row in cursor.fetchall()}
            
            # Events last 24 hours
            yesterday = (datetime.now() - timedelta(hours=24)).isoformat()
            cursor.execute('SELECT COUNT(*) FROM events WHERE timestamp >= ?', (yesterday,))
            events_24h = cursor.fetchone()[0]
            
            # Camera count
            cursor.execute('SELECT COUNT(*) FROM cameras')
            total_cameras = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM cameras WHERE status = 'online'")
            online_cameras = cursor.fetchone()[0]
            
            # Unacknowledged events
            cursor.execute('SELECT COUNT(*) FROM events WHERE acknowledged = 0')
            unacknowledged = cursor.fetchone()[0]
            
            conn.close()
            
            return jsonify({
                'total_events': total_events,
                'events_by_type': events_by_type,
                'events_by_severity': events_by_severity,
                'events_last_24h': events_24h,
                'cameras': {
                    'total': total_cameras,
                    'online': online_cameras
                },
                'unacknowledged_events': unacknowledged
            })
            
        except Exception as e:
            logger.error(f"Error getting stats: {e}")
            return jsonify({'error': str(e)}), 500
    
    # ========== Health Check ==========
    
    @app.route('/health', methods=['GET'])
    def health_check():
        """Health check endpoint"""
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'service': 'surveillance-aggregator'
        })
    
    @app.route('/', methods=['GET'])
    def index():
        """Root endpoint"""
        return jsonify({
            'service': 'D.R.I.V.E Surveillance Aggregator',
            'version': '1.0.0',
            'endpoints': {
                'events': '/api/events',
                'search': '/api/events/search',
                'cameras': '/api/cameras',
                'stats': '/api/stats',
                'health': '/health'
            }
        })
    
    return app


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Surveillance Server Aggregator')
    parser.add_argument('--host', default='0.0.0.0', help='Host to bind')
    parser.add_argument('--port', type=int, default=5001, help='Port to bind')
    parser.add_argument('--debug', action='store_true', help='Debug mode')
    
    args = parser.parse_args()
    
    app = create_app()
    
    logger.info(f"Starting Surveillance Aggregator on {args.host}:{args.port}")
    app.run(host=args.host, port=args.port, debug=args.debug)


if __name__ == "__main__":
    main()
