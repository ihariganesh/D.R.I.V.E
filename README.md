# D.R.I.V.E - Dynamic Road Intelligence & Vehicle Environment

An AI-powered traffic management system that dynamically adjusts speed limits, controls traffic lights, and manages emergency vehicle routing through intelligent multi-camera analysis.

## 🎯 Project Overview

D.R.I.V.E revolutionizes urban traffic management by:
- **Dynamically adjusting speed limits** based on real-time traffic conditions
- **Collaborative multi-camera event tracking** across city regions
- **AI-controlled traffic light optimization** for flow management
- **Emergency vehicle "Green Wave" protocol** for rapid response
- **Explainable AI dashboard** showing decision reasoning
- **Digital Twin simulation** for safe manual overrides

## 🚀 Key Innovations

### 1. **Explainable AI (XAI Dashboard)**
- Shows not just what the AI decided, but **why**
- Example: "Speed lowered to 40km/h because Camera 4 detected debris 500m ahead"
- Builds trust with traffic authorities

### 2. **Green Wave Protocol**
- Multi-camera collaborative tracking of emergency vehicles
- Proactively clears downstream intersections
- Turns lights green and lowers cross-traffic speed limits
- Also works for suspect vehicle pursuit

### 3. **Digital Twin Replay**
- 5-second predictive simulation before manual overrides
- Warns authorities if override would cause congestion
- "Predictive Human-in-the-Loop Control"

## 📁 Project Structure

```
D.R.I.V.E/
├── backend/                    # FastAPI backend services
│   ├── api/                    # REST API endpoints
│   ├── models/                 # AI/ML models
│   ├── services/               # Business logic
│   └── database/               # Database models & migrations
├── frontend/                   # React-based authority dashboard
│   ├── src/
│   │   ├── components/         # Reusable UI components
│   │   ├── pages/              # Main pages
│   │   └── services/           # API integration
├── ai-models/                  # Deep learning models
│   ├── traffic-flow/           # Traffic density analysis
│   ├── event-detection/        # Incident detection
│   ├── speed-optimization/     # Speed limit calculation
│   └── digital-twin/           # Simulation engine
├── camera-service/             # Camera integration service
├── database/                   # PostgreSQL schemas
├── docker/                     # Docker configurations
└── docs/                       # Documentation
```

## 🛠️ Technology Stack

### Backend
- **FastAPI**: High-performance async API framework
- **PostgreSQL**: Primary database with PostGIS for spatial data
- **Redis**: Caching and real-time data
- **Celery**: Asynchronous task processing

### AI/ML
- **PyTorch**: Deep learning framework
- **OpenCV**: Computer vision processing
- **YOLO v8**: Object detection
- **SHAP/LIME**: Explainable AI
- **TensorFlow**: Traffic flow prediction

### Frontend
- **React**: UI framework
- **TypeScript**: Type-safe development
- **TailwindCSS**: Styling
- **Socket.io**: Real-time updates
- **MapBox**: Interactive maps

### Infrastructure
- **Docker**: Containerization
- **Kubernetes**: Orchestration
- **Nginx**: Reverse proxy
- **Prometheus/Grafana**: Monitoring

## 🗄️ Database Schema

### Core Tables
- `cameras`: Camera locations and metadata
- `traffic_events`: Detected incidents and events
- `speed_limits`: Dynamic speed limit history
- `traffic_lights`: Light states and control
- `emergency_vehicles`: Tracked emergency vehicle data
- `manual_overrides`: Authority intervention logs
- `ai_decisions`: Decision logs with explanations
- `simulations`: Digital twin simulation results

## 🚀 Getting Started

### Prerequisites
- Python 3.10+
- Node.js 18+
- PostgreSQL 15+
- Docker & Docker Compose

### Installation

```bash
# Clone the repository
git clone https://github.com/ihariganesh/D.R.I.V.E.git
cd D.R.I.V.E

# Set up environment
cp .env.example .env

# Start with Docker Compose
docker-compose up -d

# Or run locally
# Backend
cd backend
pip install -r requirements.txt
python -m uvicorn main:app --reload

# Frontend
cd frontend
npm install
npm start
```

## 📊 Features

### For Traffic Authorities
- Real-time traffic dashboard
- Event search and playback
- Manual override controls
- Digital twin simulation preview
- XAI decision explanations

### AI Capabilities
- Traffic density estimation
- Incident detection (accidents, debris, congestion)
- Dynamic speed limit calculation
- Multi-camera vehicle tracking
- Emergency vehicle detection
- Traffic light optimization
- Predictive traffic modeling

## 🔐 Security

- Role-based access control (RBAC)
- JWT authentication
- Audit logging for all manual overrides
- Encrypted communication
- API rate limiting

## 📈 Future Enhancements

- Integration with weather APIs for condition-based adjustments
- Pedestrian flow analysis
- Public transportation prioritization
- Carbon emission optimization
- Mobile app for field officers

## 📝 License

MIT License - see LICENSE file for details

## 🤝 Contributing

Contributions are welcome! Please read CONTRIBUTING.md for guidelines.

## 👥 Team

Built with ❤️ by the D.R.I.V.E team

## 📧 Contact

For questions or support, please open an issue on GitHub.
