# 🚦 D.R.I.V.E - Dynamic Road Intelligence & Vehicle Environment

<div align="center">

![D.R.I.V.E Banner](docs/images/banner.png)

**An AI-powered centralized traffic control system with real-time surveillance and simulation capabilities.**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![React](https://img.shields.io/badge/React-18.x-61dafb.svg)](https://reactjs.org/)

</div>

---

## 🎯 Overview

D.R.I.V.E is an AI-powered centralized traffic controller that manages:
- **Traffic Lights** - Dynamic signal timing based on real-time conditions
- **Digital Sign Boards** - Display speed limits, diversion information
- **Surveillance Cameras** - AI-powered event detection and tracking

### Key Features

| Feature | Description |
|---------|-------------|
| 🚗 **Dynamic Speed Limits** | Automatically adjusts speed limits based on traffic density |
| 🚑 **Green Wave Protocol** | Priority routing for emergency vehicles (ambulances, fire trucks) |
| 👁️ **AI Surveillance** | Real-time detection of accidents, fires, running persons |
| 🔍 **Event Retrieval** | Natural language search through all camera recordings |
| 🎮 **Digital Twin** | Simulate traffic changes before applying them |

---

## 🏗️ System Architecture

The system consists of **two independent cores** that communicate with a central dashboard:

```
┌─────────────────────────────────────────────────────────────────────┐
│                        D.R.I.V.E ARCHITECTURE                        │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│   ┌──────────────────┐              ┌──────────────────┐            │
│   │    CORE A        │              │    CORE B        │            │
│   │  Traffic Sim     │              │  Surveillance    │            │
│   │   (Virtual)      │              │   (Physical)     │            │
│   ├──────────────────┤              ├──────────────────┤            │
│   │ • SUMO Simulator │              │ • YOLOv8 Detect  │            │
│   │ • TraCI Control  │              │ • OpenCV Cameras │            │
│   │ • Dynamic Speed  │              │ • Event Storage  │            │
│   │ • Green Wave     │              │ • NL Search      │            │
│   └────────┬─────────┘              └────────┬─────────┘            │
│            │                                  │                      │
│            └──────────────┬───────────────────┘                      │
│                           │                                          │
│              ┌────────────▼────────────┐                            │
│              │    Authority Dashboard   │                            │
│              │      (Streamlit)         │                            │
│              ├──────────────────────────┤                            │
│              │ • Real-time Metrics      │                            │
│              │ • Traffic Light Control  │                            │
│              │ • Event Search           │                            │
│              └──────────────────────────┘                            │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

### Core A: Traffic Simulation (Virtual)

Uses **SUMO** (Simulation of Urban MObility) controlled via Python/TraCI:
- Simulates city traffic grid with traffic lights
- Dynamic speed limit adjustment based on vehicle density
- Green Wave protocol for emergency vehicles

### Core B: Surveillance Network (Physical)

Uses **OpenCV** and **YOLOv8** for AI-powered video analysis:
- Multi-camera support (connect laptop webcams)
- Real-time object detection (people, vehicles, fire)
- Event storage and natural language search

---

## 📁 Project Structure

```
D.R.I.V.E/
├── 🖥️  backend/              # FastAPI backend server
│   ├── api/                  # API routes and schemas
│   ├── database/             # Database models
│   └── services/             # Business logic
│
├── 🎨  frontend/             # React + Vite frontend
│   └── src/
│       ├── components/
│       └── pages/
│
├── 🚗  simulation/           # SUMO Traffic Simulation (Core A)
│   ├── controller.py         # Main TraCI controller
│   └── network/              # SUMO network files
│       ├── city.net.xml      # Road network
│       ├── city.rou.xml      # Vehicle routes
│       └── city.sumocfg      # Configuration
│
├── 👁️  surveillance/         # AI Surveillance System (Core B)
│   ├── client_camera.py      # Camera client (runs on laptops)
│   ├── server_aggregator.py  # Central event server
│   └── events_db.py          # Event database operations
│
├── 📊  dashboard/            # Streamlit Authority Dashboard
│   └── app.py                # Main dashboard application
│
├── 🧠  ai_models/            # AI/ML Models
│   ├── event_detection/      # Accident/event detection
│   ├── green_wave/           # Emergency vehicle routing
│   ├── speed_optimization/   # Speed limit optimization
│   └── digital_twin/         # Traffic simulation
│
└── 📚  docs/                 # Documentation
```

---

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- Node.js 18+
- SUMO (for simulation): https://sumo.dlr.de/docs/Installing
- PostgreSQL (for production) or SQLite (for development)

### 1. Clone and Setup

```bash
git clone https://github.com/yourusername/DRIVE.git
cd DRIVE

# Install all dependencies
pip install -r backend/requirements.txt
pip install -r simulation/requirements.txt
pip install -r surveillance/requirements.txt
pip install -r dashboard/requirements.txt
```

### 2. Start All Services

```bash
# Start everything at once
./start.sh all

# Or start individual components:
./start.sh backend      # Backend API
./start.sh frontend     # React frontend
./start.sh simulation   # SUMO traffic simulation
./start.sh surveillance # Surveillance server
./start.sh dashboard    # Streamlit dashboard
```

### 3. Access the System

| Service | URL |
|---------|-----|
| Frontend | http://localhost:5173 |
| Backend API | http://localhost:8000 |
| API Docs | http://localhost:8000/docs |
| Streamlit Dashboard | http://localhost:8501 |
| Surveillance API | http://localhost:5001 |

---

## 📖 Module Documentation

### Module A: SUMO Traffic Controller

```bash
cd simulation
python controller.py --gui  # With SUMO GUI
python controller.py --nogui  # Headless mode
```

**Features:**
- Monitors vehicle density on each edge
- When density > 30 vehicles: reduces speed to 30 km/h
- Detects ambulances and forces green lights ahead

### Module B: Surveillance System

**Start the Server:**
```bash
cd surveillance
python server_aggregator.py --host 0.0.0.0 --port 5001
```

**Connect a Camera (on each laptop):**
```bash
python client_camera.py \
  --camera-id CAM001 \
  --server http://<server-ip>:5001 \
  --location "Main Street"
```

### Module C: Authority Dashboard

```bash
cd dashboard
streamlit run app.py
```

**Features:**
- **Tab 1 - Traffic**: Live speed metrics, force red/green lights
- **Tab 2 - Surveillance**: Natural language event search

---

## 🔍 Natural Language Event Search

Search surveillance events using natural language:

| Query | What it finds |
|-------|---------------|
| `"person"` | All person detections |
| `"fire in last hour"` | Fire events in the last hour |
| `"running person camera 1"` | Running persons from Camera 1 |
| `"accident yesterday"` | Accidents from yesterday |
| `"truck"` | All truck detections |

---

## 🌐 API Endpoints

### Backend API (FastAPI)

```
GET  /api/v1/dashboard/overview   # Dashboard stats
POST /api/v1/simulations/run      # Run digital twin
GET  /api/v1/cameras              # List cameras
POST /api/v1/events               # Create event
GET  /api/v1/emergency/vehicles   # Active emergencies
```

### Surveillance API (Flask)

```
POST /api/events           # Receive event from camera
GET  /api/events           # List events
GET  /api/events/search    # Natural language search
GET  /api/cameras          # List cameras
GET  /api/stats            # Get statistics
```

---

## 🧪 Running Tests

```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm test
```

---

## 🐳 Docker Deployment

```bash
# Build and run with Docker Compose
docker-compose up --build

# Or just the database
docker-compose -f docker-compose.db.yml up -d
```

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 👥 Team

Built with ❤️ by the D.R.I.V.E Team

---

<div align="center">

**🚦 D.R.I.V.E - Making Roads Safer, Smarter, and More Efficient 🚦**

</div>
