# D.R.I.V.E Setup Guide

## Prerequisites

- Docker & Docker Compose
- PostgreSQL 15+
- Python 3.10+
- Node.js 18+

## Quick Start with Docker

1. **Clone the repository**
```bash
git clone https://github.com/ihariganesh/D.R.I.V.E.git
cd D.R.I.V.E
```

2. **Set up environment variables**
```bash
cp .env.example .env
# Edit .env with your settings
```

3. **Start all services**
```bash
docker-compose up -d
```

4. **Initialize the database**
```bash
docker exec -i drive-postgres psql -U postgres drive_db < database/schema.sql
docker exec -i drive-postgres psql -U postgres drive_db < database/seed_data.sql
```

5. **Access the application**
- Frontend: http://localhost:3000
- API Docs: http://localhost:8000/docs
- Login: admin / password123

## Development Setup (Without Docker)

### Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

### Database Setup

```bash
psql -U postgres -c "CREATE DATABASE drive_db;"
psql -U postgres drive_db < database/schema.sql
psql -U postgres drive_db < database/seed_data.sql
```

## Configuration

### Database Configuration
Edit `.env` file:
```
DB_HOST=localhost
DB_PORT=5432
DB_NAME=drive_db
DB_USER=postgres
DB_PASSWORD=your_password
```

### API Configuration
```
API_HOST=0.0.0.0
API_PORT=8000
API_SECRET_KEY=your_secret_key_here
```

## Key Features Setup

### 1. Explainable AI (XAI) Dashboard
- Access at: `/decisions`
- Shows AI decision reasoning
- No additional setup required

### 2. Green Wave Protocol
- Access at: `/emergency`
- Requires emergency vehicle registration
- Activate through API or UI

### 3. Digital Twin Simulation
- Access at: `/simulations`
- Run before manual overrides
- Predicts traffic impact

## Testing

### Run Backend Tests
```bash
cd backend
pytest
```

### Run Frontend Tests
```bash
cd frontend
npm test
```

## Troubleshooting

### Database Connection Issues
- Verify PostgreSQL is running
- Check connection credentials in `.env`
- Ensure PostGIS extension is installed

### Camera Service Issues
- Check camera permissions
- Verify camera IDs in database
- Review camera service logs

### Frontend Build Issues
- Clear node_modules: `rm -rf node_modules && npm install`
- Clear cache: `npm cache clean --force`

## Production Deployment

### 1. Update environment variables for production
### 2. Enable SSL/HTTPS
### 3. Set up monitoring (Prometheus/Grafana)
### 4. Configure backup strategies
### 5. Set up CI/CD pipeline

## Support

For issues and questions:
- GitHub Issues: https://github.com/ihariganesh/D.R.I.V.E/issues
- Documentation: /docs
