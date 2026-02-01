"""
Events Database - Surveillance Network Core B
Database operations for events storage and retrieval
"""

import sqlite3
import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from dataclasses import dataclass


@dataclass
class Event:
    """Event data model"""
    id: Optional[int] = None
    event_type: str = ""
    confidence: float = 0.0
    timestamp: str = ""
    camera_id: str = ""
    location: Optional[str] = None
    bounding_box: Optional[List[int]] = None
    description: Optional[str] = None
    frame_number: int = 0
    severity: str = "low"
    acknowledged: bool = False


class EventsDatabase:
    """Database manager for surveillance events"""
    
    def __init__(self, db_path: str = "events.db"):
        self.db_path = db_path
        self._init_db()
    
    def _init_db(self):
        """Initialize database schema"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_type TEXT NOT NULL,
                confidence REAL DEFAULT 0.0,
                timestamp TEXT NOT NULL,
                camera_id TEXT NOT NULL,
                location TEXT,
                bounding_box TEXT,
                description TEXT,
                frame_number INTEGER DEFAULT 0,
                severity TEXT DEFAULT 'low',
                acknowledged INTEGER DEFAULT 0,
                acknowledged_by TEXT,
                acknowledged_at TEXT
            )
        ''')
        
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_event_type ON events(event_type)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_camera_id ON events(camera_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_timestamp ON events(timestamp)')
        
        conn.commit()
        conn.close()
    
    def _get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def insert_event(self, event: Event) -> int:
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO events 
            (event_type, confidence, timestamp, camera_id, location, 
             bounding_box, description, frame_number, severity)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            event.event_type, event.confidence, event.timestamp,
            event.camera_id, event.location,
            json.dumps(event.bounding_box) if event.bounding_box else None,
            event.description, event.frame_number, event.severity
        ))
        
        event_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return event_id
    
    def search_events(self, query: str, limit: int = 100) -> List[Event]:
        """Search events using text query"""
        query_lower = query.lower()
        
        keywords = {
            'person': 'person', 'car': 'car', 'truck': 'truck',
            'fire': 'fire', 'running': 'person_running', 'accident': 'accident'
        }
        
        event_types = [et for kw, et in keywords.items() if kw in query_lower]
        
        conn = self._get_connection()
        cursor = conn.cursor()
        
        if event_types:
            placeholders = ','.join(['?' for _ in event_types])
            sql = f'SELECT * FROM events WHERE event_type IN ({placeholders}) ORDER BY timestamp DESC LIMIT ?'
            cursor.execute(sql, event_types + [limit])
        else:
            cursor.execute('SELECT * FROM events WHERE description LIKE ? ORDER BY timestamp DESC LIMIT ?',
                          (f'%{query}%', limit))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [self._row_to_event(row) for row in rows]
    
    def _row_to_event(self, row) -> Event:
        bbox = json.loads(row['bounding_box']) if row['bounding_box'] else None
        return Event(
            id=row['id'], event_type=row['event_type'], confidence=row['confidence'],
            timestamp=row['timestamp'], camera_id=row['camera_id'], location=row['location'],
            bounding_box=bbox, description=row['description'], frame_number=row['frame_number'],
            severity=row['severity'], acknowledged=bool(row['acknowledged'])
        )
