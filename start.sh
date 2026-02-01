#!/bin/bash
# D.R.I.V.E - Quick Start Script
# Starts all components of the traffic management system

set -e

echo "🚦 D.R.I.V.E - Dynamic Road Intelligence & Vehicle Environment"
echo "=============================================================="
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Check dependencies
check_dependency() {
    if ! command -v $1 &> /dev/null; then
        echo -e "${RED}❌ $1 is not installed${NC}"
        return 1
    fi
    echo -e "${GREEN}✓ $1 found${NC}"
    return 0
}

echo -e "${BLUE}Checking dependencies...${NC}"
check_dependency python3
check_dependency npm

# Function to start a service
start_service() {
    local name=$1
    local dir=$2
    local cmd=$3
    local logfile=$4
    
    echo -e "${YELLOW}Starting $name...${NC}"
    cd "$SCRIPT_DIR/$dir"
    
    if [ -f "requirements.txt" ]; then
        pip install -q -r requirements.txt 2>/dev/null || true
    fi
    
    nohup $cmd > "$logfile" 2>&1 &
    echo $! > ".pid"
    echo -e "${GREEN}✓ $name started (PID: $!)${NC}"
    
    cd "$SCRIPT_DIR"
}

# Parse arguments
MODE=${1:-all}

case $MODE in
    "backend")
        echo -e "\n${BLUE}=== Starting Backend Only ===${NC}\n"
        cd backend
        pip install -q -r requirements.txt
        python main.py
        ;;
    
    "frontend")
        echo -e "\n${BLUE}=== Starting Frontend Only ===${NC}\n"
        cd frontend
        npm install
        npm run dev
        ;;
    
    "simulation")
        echo -e "\n${BLUE}=== Starting SUMO Simulation ===${NC}\n"
        cd simulation
        pip install -q -r requirements.txt
        python controller.py --gui
        ;;
    
    "surveillance")
        echo -e "\n${BLUE}=== Starting Surveillance Server ===${NC}\n"
        cd surveillance
        pip install -q -r requirements.txt
        python server_aggregator.py
        ;;
    
    "camera")
        CAM_ID=${2:-CAM001}
        echo -e "\n${BLUE}=== Starting Camera Client ($CAM_ID) ===${NC}\n"
        cd surveillance
        pip install -q -r requirements.txt
        python client_camera.py --camera-id $CAM_ID --server http://localhost:5001
        ;;
    
    "dashboard")
        echo -e "\n${BLUE}=== Starting Streamlit Dashboard ===${NC}\n"
        cd dashboard
        pip install -q -r requirements.txt
        streamlit run app.py
        ;;
    
    "all")
        echo -e "\n${BLUE}=== Starting All Services ===${NC}\n"
        
        # Start Backend
        start_service "Backend API" "backend" "python main.py" "backend.log"
        sleep 2
        
        # Start Surveillance Server
        start_service "Surveillance Server" "surveillance" "python server_aggregator.py" "server.log"
        sleep 1
        
        # Start Frontend
        echo -e "${YELLOW}Starting Frontend...${NC}"
        cd frontend
        npm install --silent
        nohup npm run dev > ../frontend.log 2>&1 &
        echo $! > .pid
        echo -e "${GREEN}✓ Frontend started${NC}"
        cd "$SCRIPT_DIR"
        sleep 2
        
        # Start Dashboard
        start_service "Streamlit Dashboard" "dashboard" "streamlit run app.py --server.port 8501" "dashboard.log"
        
        echo ""
        echo -e "${GREEN}============================================${NC}"
        echo -e "${GREEN}All services started!${NC}"
        echo -e "${GREEN}============================================${NC}"
        echo ""
        echo "Services available at:"
        echo -e "  ${BLUE}• Backend API:${NC}        http://localhost:8000"
        echo -e "  ${BLUE}• Frontend:${NC}           http://localhost:5173"
        echo -e "  ${BLUE}• Surveillance API:${NC}   http://localhost:5001"
        echo -e "  ${BLUE}• Streamlit Dashboard:${NC} http://localhost:8501"
        echo ""
        echo "To start SUMO simulation: ./start.sh simulation"
        echo "To connect a camera:      ./start.sh camera CAM001"
        echo ""
        ;;
    
    "stop")
        echo -e "\n${BLUE}=== Stopping All Services ===${NC}\n"
        
        for dir in backend surveillance frontend dashboard; do
            if [ -f "$dir/.pid" ]; then
                PID=$(cat "$dir/.pid")
                if kill -0 $PID 2>/dev/null; then
                    kill $PID
                    echo -e "${GREEN}✓ Stopped $dir (PID: $PID)${NC}"
                fi
                rm "$dir/.pid"
            fi
        done
        
        echo -e "\n${GREEN}All services stopped${NC}"
        ;;
    
    *)
        echo "Usage: ./start.sh [mode]"
        echo ""
        echo "Modes:"
        echo "  all          - Start all services (default)"
        echo "  backend      - Start backend API only"
        echo "  frontend     - Start frontend only"
        echo "  simulation   - Start SUMO simulation"
        echo "  surveillance - Start surveillance server"
        echo "  camera CAM_ID - Start camera client"
        echo "  dashboard    - Start Streamlit dashboard"
        echo "  stop         - Stop all services"
        ;;
esac
