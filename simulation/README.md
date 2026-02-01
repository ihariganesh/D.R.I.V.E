# SUMO Traffic Simulation - Core A

This module contains the SUMO (Simulation of Urban MObility) traffic simulation controlled by Python/TraCI.

## Features

- **Dynamic Speed Limits**: Automatically adjusts speed limits based on traffic density
- **Green Wave Protocol**: Priority routing for emergency vehicles (ambulances)
- **Real-time Traffic Monitoring**: Tracks vehicle counts, speeds, and congestion

## Requirements

1. Install SUMO: https://sumo.dlr.de/docs/Installing/index.html
2. Install Python dependencies: `pip install traci sumolib`

## Directory Structure

```
simulation/
├── controller.py      # Main TraCI controller script
├── network/           # SUMO network files
│   ├── city.net.xml   # City road network
│   ├── city.rou.xml   # Vehicle routes
│   └── city.sumocfg   # SUMO configuration
├── scenarios/         # Test scenarios
└── README.md          # This file
```

## Usage

```bash
# Start simulation with GUI
python controller.py --gui

# Start simulation without GUI (faster)
python controller.py --nogui

# Run specific scenario
python controller.py --scenario congestion
```

## Configuration

See `controller.py` for configuration options:
- `DENSITY_THRESHOLD`: Vehicle density to trigger speed reduction (default: 30)
- `LOW_SPEED_LIMIT`: Reduced speed limit during congestion (default: 30 km/h)
- `NORMAL_SPEED_LIMIT`: Normal speed limit (default: 50 km/h)
