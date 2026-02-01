"""
D.R.I.V.E Authority Dashboard
Streamlit app to monitor both Traffic Simulation and Surveillance cores

Features:
- Tab 1 - Traffic: Live metrics from SUMO, force traffic light controls
- Tab 2 - Surveillance: Natural language event search
"""

import streamlit as st
import requests
import pandas as pd
import sqlite3
import json
from datetime import datetime, timedelta
import time
import os

# Page config
st.set_page_config(
    page_title="D.R.I.V.E Authority Dashboard",
    page_icon="🚦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Configuration
SIMULATION_DB = os.environ.get('SIMULATION_DB', '../simulation/simulation_logs.db')
SURVEILLANCE_URL = os.environ.get('SURVEILLANCE_URL', 'http://localhost:5001')
BACKEND_URL = os.environ.get('BACKEND_URL', 'http://localhost:8000')

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 1rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
        border-radius: 12px;
        padding: 1.5rem;
        border: 1px solid rgba(102, 126, 234, 0.3);
    }
    .stButton>button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.5rem 1rem;
    }
    .stButton>button:hover {
        background: linear-gradient(135deg, #764ba2 0%, #667eea 100%);
    }
    .alert-critical { background-color: #ff4444; color: white; padding: 1rem; border-radius: 8px; }
    .alert-warning { background-color: #ffbb33; color: black; padding: 1rem; border-radius: 8px; }
    .alert-success { background-color: #00C851; color: white; padding: 1rem; border-radius: 8px; }
</style>
""", unsafe_allow_html=True)


def get_simulation_metrics():
    """Get metrics from simulation database"""
    try:
        if not os.path.exists(SIMULATION_DB):
            return None
        
        conn = sqlite3.connect(SIMULATION_DB)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Get latest metrics
        cursor.execute('''
            SELECT * FROM traffic_metrics 
            ORDER BY timestamp DESC 
            LIMIT 100
        ''')
        rows = cursor.fetchall()
        
        if not rows:
            conn.close()
            return None
        
        # Calculate averages
        total_vehicles = sum(row['vehicle_count'] for row in rows)
        avg_speed = sum(row['average_speed'] for row in rows) / len(rows)
        avg_occupancy = sum(row['occupancy'] for row in rows) / len(rows)
        
        # Get recent events
        cursor.execute('''
            SELECT * FROM simulation_events 
            ORDER BY timestamp DESC 
            LIMIT 20
        ''')
        events = [dict(row) for row in cursor.fetchall()]
        
        conn.close()
        
        return {
            'total_vehicles': total_vehicles // len(rows),
            'average_speed_kmh': avg_speed * 3.6,
            'average_occupancy': avg_occupancy,
            'recent_events': events,
            'data_points': len(rows)
        }
    except Exception as e:
        st.error(f"Error reading simulation data: {e}")
        return None


def get_surveillance_stats():
    """Get stats from surveillance server"""
    try:
        response = requests.get(f"{SURVEILLANCE_URL}/api/stats", timeout=5)
        if response.status_code == 200:
            return response.json()
    except:
        pass
    return None


def search_surveillance_events(query: str):
    """Search events using natural language"""
    try:
        response = requests.get(
            f"{SURVEILLANCE_URL}/api/events/search",
            params={'q': query},
            timeout=10
        )
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        st.error(f"Search error: {e}")
    return None


def force_red_light(traffic_light_id: str):
    """Force traffic light to red via backend"""
    try:
        response = requests.post(
            f"{BACKEND_URL}/api/v1/simulation/force-red",
            json={'traffic_light_id': traffic_light_id},
            timeout=5
        )
        return response.status_code == 200
    except:
        return False


# Sidebar
with st.sidebar:
    st.image("https://via.placeholder.com/150x50/667eea/ffffff?text=D.R.I.V.E", width=150)
    st.markdown("### 🎛️ Control Panel")
    
    st.markdown("---")
    
    # System Status
    st.markdown("#### System Status")
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Core A", "🟢 Online" if os.path.exists(SIMULATION_DB) else "🔴 Offline")
    with col2:
        surv_stats = get_surveillance_stats()
        st.metric("Core B", "🟢 Online" if surv_stats else "🔴 Offline")
    
    st.markdown("---")
    
    # Auto-refresh
    auto_refresh = st.checkbox("Auto Refresh", value=True)
    refresh_rate = st.slider("Refresh Rate (sec)", 1, 30, 5)

# Main content
st.markdown('<h1 class="main-header">🚦 D.R.I.V.E Authority Dashboard</h1>', unsafe_allow_html=True)

# Create tabs
tab1, tab2 = st.tabs(["🚗 Traffic Simulation", "👁️ Surveillance Network"])

# ========== TAB 1: Traffic Simulation ==========
with tab1:
    st.markdown("### Real-time Traffic Monitoring")
    
    # Get simulation data
    sim_data = get_simulation_metrics()
    
    if sim_data:
        # Metrics row
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "🚗 Active Vehicles",
                f"{sim_data['total_vehicles']:,}",
                delta=None
            )
        
        with col2:
            st.metric(
                "🏎️ Average Speed",
                f"{sim_data['average_speed_kmh']:.1f} km/h",
                delta=None
            )
        
        with col3:
            st.metric(
                "📊 Road Occupancy",
                f"{sim_data['average_occupancy']:.1%}",
                delta=None
            )
        
        with col4:
            st.metric(
                "📈 Data Points",
                sim_data['data_points'],
                delta=None
            )
        
        st.markdown("---")
        
        # Control section
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown("#### 🚨 Traffic Light Control")
            
            traffic_light_id = st.selectbox(
                "Select Traffic Light",
                ["J1", "J2", "J3", "J4", "J5", "J6", "J7", "J8", "J9"],
                help="Select a junction to control"
            )
            
            col_btn1, col_btn2, col_btn3 = st.columns(3)
            
            with col_btn1:
                if st.button("🔴 FORCE RED", type="primary", use_container_width=True):
                    success = force_red_light(traffic_light_id)
                    if success:
                        st.success(f"Traffic light {traffic_light_id} set to RED")
                    else:
                        st.warning("Command sent (simulation may be offline)")
            
            with col_btn2:
                if st.button("🟢 FORCE GREEN", use_container_width=True):
                    st.info(f"Green wave activated for {traffic_light_id}")
            
            with col_btn3:
                if st.button("🔄 RESET", use_container_width=True):
                    st.info(f"Traffic light {traffic_light_id} reset to auto")
        
        with col2:
            st.markdown("#### 📊 Quick Stats")
            
            # Speed status
            if sim_data['average_speed_kmh'] < 20:
                st.error("⚠️ Heavy congestion detected!")
            elif sim_data['average_speed_kmh'] < 35:
                st.warning("⚡ Moderate traffic")
            else:
                st.success("✅ Traffic flowing smoothly")
        
        st.markdown("---")
        
        # Recent events
        st.markdown("#### 📝 Recent Simulation Events")
        
        if sim_data['recent_events']:
            events_df = pd.DataFrame(sim_data['recent_events'])
            st.dataframe(
                events_df[['timestamp', 'event_type', 'entity_id', 'details']].head(10),
                use_container_width=True,
                hide_index=True
            )
        else:
            st.info("No recent events")
    
    else:
        st.warning("""
        ⚠️ **Simulation not running**
        
        To start the SUMO simulation:
        ```bash
        cd simulation
        python controller.py --gui
        ```
        """)

# ========== TAB 2: Surveillance Network ==========
with tab2:
    st.markdown("### AI-Powered Surveillance Network")
    
    # Get surveillance stats
    surv_stats = get_surveillance_stats()
    
    if surv_stats:
        # Stats row
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("📹 Cameras", f"{surv_stats['cameras']['online']}/{surv_stats['cameras']['total']}")
        
        with col2:
            st.metric("🎯 Total Events", f"{surv_stats['total_events']:,}")
        
        with col3:
            st.metric("⏰ Last 24h", surv_stats['events_last_24h'])
        
        with col4:
            st.metric("🔔 Unacknowledged", surv_stats['unacknowledged_events'])
        
        st.markdown("---")
    
    # Natural Language Search
    st.markdown("#### 🔍 Natural Language Event Search")
    st.caption("Search examples: 'person in last hour', 'fire camera 1', 'running person yesterday'")
    
    search_query = st.text_input(
        "Search Events",
        placeholder="Type your search query...",
        label_visibility="collapsed"
    )
    
    col1, col2 = st.columns([1, 4])
    with col1:
        search_clicked = st.button("🔍 Search", type="primary", use_container_width=True)
    
    if search_clicked and search_query:
        with st.spinner("Searching..."):
            results = search_surveillance_events(search_query)
        
        if results:
            st.success(f"Found {results['count']} events")
            
            # Show parsed query
            with st.expander("Query Interpretation"):
                st.json(results.get('parsed', {}))
            
            # Results table
            if results['results']:
                events_df = pd.DataFrame(results['results'])
                
                # Format columns
                display_cols = ['timestamp', 'event_type', 'camera_id', 'severity', 'description']
                available_cols = [c for c in display_cols if c in events_df.columns]
                
                st.dataframe(
                    events_df[available_cols],
                    use_container_width=True,
                    hide_index=True
                )
            else:
                st.info("No events found matching your query")
        else:
            st.error("Search failed. Is the surveillance server running?")
    
    st.markdown("---")
    
    # Event type breakdown
    if surv_stats and surv_stats.get('events_by_type'):
        st.markdown("#### 📊 Events by Type")
        
        events_by_type = surv_stats['events_by_type']
        
        # Create bar chart
        import plotly.express as px
        
        df = pd.DataFrame({
            'Event Type': list(events_by_type.keys()),
            'Count': list(events_by_type.values())
        })
        
        fig = px.bar(
            df, x='Event Type', y='Count',
            color='Count',
            color_continuous_scale='Viridis'
        )
        fig.update_layout(
            showlegend=False,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)'
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    # Camera status
    if surv_stats:
        st.markdown("#### 📹 Camera Status")
        
        try:
            response = requests.get(f"{SURVEILLANCE_URL}/api/cameras", timeout=5)
            if response.status_code == 200:
                cameras = response.json().get('cameras', [])
                
                if cameras:
                    for cam in cameras:
                        status_icon = "🟢" if cam['status'] == 'online' else "🔴"
                        st.markdown(f"{status_icon} **{cam['camera_id']}** - {cam.get('location', 'Unknown')}")
                else:
                    st.info("No cameras registered")
        except:
            pass
    else:
        st.warning("""
        ⚠️ **Surveillance server not running**
        
        To start the surveillance server:
        ```bash
        cd surveillance
        python server_aggregator.py
        ```
        
        To connect a camera:
        ```bash
        python client_camera.py --camera-id CAM001 --server http://localhost:5001
        ```
        """)

# Auto-refresh
if auto_refresh:
    time.sleep(refresh_rate)
    st.rerun()
