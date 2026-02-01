"""
Surveillance Network - Core B
AI-powered video surveillance with event detection
"""

from .client_camera import CameraClient
from .server_aggregator import create_app
from .events_db import EventsDatabase

__all__ = ['CameraClient', 'create_app', 'EventsDatabase']
