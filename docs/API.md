# D.R.I.V.E API Documentation

## Authentication

All API endpoints require JWT authentication.

### Login
```http
POST /api/v1/users/login
Content-Type: application/json

{
  "username": "admin",
  "password": "password123"
}
```

Response:
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer"
}
```

Use the token in subsequent requests:
```http
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc...
```

## Core Endpoints

### Cameras

#### List Cameras
```http
GET /api/v1/cameras?region=Central&status=active
```

#### Get Camera Details
```http
GET /api/v1/cameras/{camera_id}
```

#### Find Nearby Cameras
```http
GET /api/v1/cameras/nearby/{lat}/{lon}?radius=1000
```

### Traffic Events

#### List Events
```http
GET /api/v1/events?event_type=accident&status=active
```

#### Create Event
```http
POST /api/v1/events
Content-Type: application/json

{
  "event_type": "accident",
  "severity": "high",
  "location": {"lat": 12.9716, "lon": 77.5946},
  "description": "Multi-vehicle accident"
}
```

#### Acknowledge Event
```http
PATCH /api/v1/events/{event_id}/acknowledge
```

### AI Decisions (XAI)

#### List Decisions
```http
GET /api/v1/decisions?decision_type=speed_limit_change
```

#### Get Decision Explanation
```http
GET /api/v1/decisions/{decision_id}/explanation
```

Response:
```json
{
  "decision_id": "uuid",
  "decision_type": "speed_limit_change",
  "what": {"new_limit": 40, "old_limit": 60},
  "why": "Speed reduced to 40 km/h due to road maintenance detected 500m ahead by Camera CAM001",
  "confidence": 0.85,
  "detailed_reasoning": {...}
}
```

### Emergency & Green Wave

#### Activate Green Wave
```http
POST /api/v1/emergency/green-wave/activate
Content-Type: application/json

{
  "vehicle_id": "uuid",
  "route": [
    {"lat": 12.9716, "lon": 77.5946},
    {"lat": 12.9750, "lon": 77.6050}
  ],
  "priority": 1
}
```

Response:
```json
{
  "message": "Green Wave Protocol activated",
  "affected_lights": ["TL001", "TL002"],
  "affected_signs": ["SB001"],
  "eta_improvement_seconds": 60
}
```

#### Deactivate Green Wave
```http
POST /api/v1/emergency/green-wave/deactivate/{vehicle_id}
```

### Digital Twin Simulations

#### Run Simulation
```http
POST /api/v1/simulations/run
Content-Type: application/json

{
  "simulation_type": "manual_override",
  "scenario_description": "Force red light on TL001",
  "input_state": {
    "traffic_metrics": {...},
    "traffic_lights": {...}
  },
  "proposed_changes": {
    "override_type": "traffic_light",
    "entity_id": "TL001",
    "new_value": "red"
  },
  "simulation_duration": 5
}
```

Response:
```json
{
  "id": "uuid",
  "recommendation": "approve|caution|reject",
  "warnings": [
    {
      "severity": "high",
      "message": "Override may cause 30%+ increase in congestion"
    }
  ],
  "predicted_metrics": {
    "congestion_level": 0.75,
    "queue_length": 45
  }
}
```

#### Approve Simulation
```http
POST /api/v1/simulations/{simulation_id}/approve
Content-Type: application/json

{
  "override_type": "traffic_light",
  "entity_id": "TL001",
  "reason": "Emergency situation",
  "duration_minutes": 15
}
```

## WebSocket Events

Connect to WebSocket:
```javascript
const ws = new WebSocket('ws://localhost:8000/ws/{client_id}');

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  // Handle real-time updates
};
```

Event Types:
- `new_event`: New traffic event detected
- `event_resolved`: Event resolved
- `green_wave_activated`: Green Wave protocol activated
- `green_wave_deactivated`: Green Wave deactivated
- `ai_decision`: New AI decision made

## Error Responses

All errors follow this format:
```json
{
  "detail": "Error message"
}
```

Status Codes:
- `200`: Success
- `201`: Created
- `400`: Bad Request
- `401`: Unauthorized
- `403`: Forbidden
- `404`: Not Found
- `500`: Internal Server Error
