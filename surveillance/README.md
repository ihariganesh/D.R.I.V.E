# Surveillance Network - Core B

This module contains the AI-powered surveillance system for event detection and tracking.

## Features

- **Real-time Object Detection**: Uses YOLOv8 to detect persons, vehicles, fire, etc.
- **Event Classification**: Detects accidents, theft (running persons), fires
- **Multi-Camera Support**: Connects multiple laptop cameras to central server
- **Natural Language Event Retrieval**: Search events with natural language queries

## Architecture

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   Camera 1      │     │   Camera 2      │     │   Camera N      │
│ (Laptop/Webcam) │     │ (Laptop/Webcam) │     │ (Laptop/Webcam) │
└────────┬────────┘     └────────┬────────┘     └────────┬────────┘
         │                       │                       │
         │  HTTP/WebSocket       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌────────────▼────────────┐
                    │   Server Aggregator     │
                    │   (FastAPI/Flask)       │
                    │                         │
                    │   - Receives events     │
                    │   - Stores in SQLite    │
                    │   - Provides search API │
                    └────────────┬────────────┘
                                 │
                    ┌────────────▼────────────┐
                    │   SQLite Database       │
                    │   (events.db)           │
                    └─────────────────────────┘
```

## Files

- `client_camera.py` - Runs on each laptop/camera client
- `server_aggregator.py` - Central server for event aggregation
- `events_db.py` - Database models and queries
- `event_search.py` - Natural language event search

## Usage

### Start the Server
```bash
python server_aggregator.py --host 0.0.0.0 --port 5001
```

### Start a Camera Client
```bash
# On each laptop
python client_camera.py --server http://192.168.1.100:5001 --camera-id CAM001
```

## Event Types Detected

| Event Type | Detection Method |
|------------|------------------|
| Person | YOLOv8 object detection |
| Vehicle | YOLOv8 object detection |
| Fire | YOLOv8 + color analysis |
| Running Person | Motion analysis + pose estimation |
| Accident | Vehicle clustering + sudden stop |
| Theft | Running person + abnormal behavior |
