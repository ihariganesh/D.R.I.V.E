#!/bin/bash
# Starts D.R.I.V.E with Bangalore Map
set -e

echo "🚦 D.R.I.V.E - Bangalore Simulation Mode"
echo "======================================="

# Ensure map exists
if [ ! -f "simulation/network/bangalore.net.xml" ]; then
    echo "Map not found. Running setup..."
    cd simulation
    python3 setup_bangalore.py
    cd ..
fi

echo "Starting Simulation (GUI)..."
cd simulation
# Using & to run in background so shell doesn't block, but for user demo maybe foreground is better?
# Use nohup for backend/dashboard, but foreground for simulation GUI often makes sense.
# But let's follow start.sh pattern.

# Start Backend
echo "Starting Backend..."
cd ../backend
nohup python main.py > backend.log 2>&1 &
echo $! > .pid
cd ../simulation

# Start Dashboard
echo "Starting Dashboard..."
cd ../dashboard
nohup streamlit run app.py --server.port 8501 > dashboard.log 2>&1 &
echo $! > .pid
cd ../simulation

# Start Simulation with Bangalore Config
echo "Launching SUMO with Central Bangalore Map (MG Road / Cubbon Park)..."
python3 controller.py --config network/bangalore.sumocfg --gui

# Cleanup on exit
cd ..
./start.sh stop
