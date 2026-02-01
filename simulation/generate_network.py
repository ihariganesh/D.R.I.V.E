#!/usr/bin/env python3
"""
Generate simple SUMO network for D.R.I.V.E testing
Creates a 3x3 grid with traffic lights
"""

import os
import subprocess

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
NETWORK_DIR = os.path.join(SCRIPT_DIR, 'network')

# Node definitions (junctions)
NODES = """<?xml version="1.0" encoding="UTF-8"?>
<nodes>
    <!-- 3x3 Grid of intersections with traffic lights -->
    <node id="J1" x="0.0"   y="0.0"   type="traffic_light"/>
    <node id="J2" x="200.0" y="0.0"   type="traffic_light"/>
    <node id="J3" x="400.0" y="0.0"   type="traffic_light"/>
    <node id="J4" x="0.0"   y="200.0" type="traffic_light"/>
    <node id="J5" x="200.0" y="200.0" type="traffic_light"/>
    <node id="J6" x="400.0" y="200.0" type="traffic_light"/>
    <node id="J7" x="0.0"   y="400.0" type="traffic_light"/>
    <node id="J8" x="200.0" y="400.0" type="traffic_light"/>
    <node id="J9" x="400.0" y="400.0" type="traffic_light"/>
    
    <!-- Entry/Exit points -->
    <node id="W1" x="-100.0" y="0.0"   type="priority"/>
    <node id="W2" x="-100.0" y="200.0" type="priority"/>
    <node id="W3" x="-100.0" y="400.0" type="priority"/>
    <node id="E1" x="500.0"  y="0.0"   type="priority"/>
    <node id="E2" x="500.0"  y="200.0" type="priority"/>
    <node id="E3" x="500.0"  y="400.0" type="priority"/>
    <node id="S1" x="0.0"    y="-100.0" type="priority"/>
    <node id="S2" x="200.0"  y="-100.0" type="priority"/>
    <node id="S3" x="400.0"  y="-100.0" type="priority"/>
    <node id="N1" x="0.0"    y="500.0" type="priority"/>
    <node id="N2" x="200.0"  y="500.0" type="priority"/>
    <node id="N3" x="400.0"  y="500.0" type="priority"/>
</nodes>
"""

# Edge definitions (roads)
EDGES = """<?xml version="1.0" encoding="UTF-8"?>
<edges>
    <!-- Horizontal roads (West-East) -->
    <edge id="W1-J1" from="W1" to="J1" numLanes="2" speed="13.89"/>
    <edge id="J1-J2" from="J1" to="J2" numLanes="2" speed="13.89"/>
    <edge id="J2-J3" from="J2" to="J3" numLanes="2" speed="13.89"/>
    <edge id="J3-E1" from="J3" to="E1" numLanes="2" speed="13.89"/>
    
    <edge id="W2-J4" from="W2" to="J4" numLanes="2" speed="13.89"/>
    <edge id="J4-J5" from="J4" to="J5" numLanes="2" speed="13.89"/>
    <edge id="J5-J6" from="J5" to="J6" numLanes="2" speed="13.89"/>
    <edge id="J6-E2" from="J6" to="E2" numLanes="2" speed="13.89"/>
    
    <edge id="W3-J7" from="W3" to="J7" numLanes="2" speed="13.89"/>
    <edge id="J7-J8" from="J7" to="J8" numLanes="2" speed="13.89"/>
    <edge id="J8-J9" from="J8" to="J9" numLanes="2" speed="13.89"/>
    <edge id="J9-E3" from="J9" to="E3" numLanes="2" speed="13.89"/>
    
    <!-- Reverse horizontal -->
    <edge id="J1-W1" from="J1" to="W1" numLanes="2" speed="13.89"/>
    <edge id="J2-J1" from="J2" to="J1" numLanes="2" speed="13.89"/>
    <edge id="J3-J2" from="J3" to="J2" numLanes="2" speed="13.89"/>
    <edge id="E1-J3" from="E1" to="J3" numLanes="2" speed="13.89"/>
    
    <!-- Vertical roads (South-North) -->
    <edge id="S1-J1" from="S1" to="J1" numLanes="2" speed="13.89"/>
    <edge id="J1-J4" from="J1" to="J4" numLanes="2" speed="13.89"/>
    <edge id="J4-J7" from="J4" to="J7" numLanes="2" speed="13.89"/>
    <edge id="J7-N1" from="J7" to="N1" numLanes="2" speed="13.89"/>
    
    <edge id="S2-J2" from="S2" to="J2" numLanes="2" speed="13.89"/>
    <edge id="J2-J5" from="J2" to="J5" numLanes="2" speed="13.89"/>
    <edge id="J5-J8" from="J5" to="J8" numLanes="2" speed="13.89"/>
    <edge id="J8-N2" from="J8" to="N2" numLanes="2" speed="13.89"/>
    
    <edge id="S3-J3" from="S3" to="J3" numLanes="2" speed="13.89"/>
    <edge id="J3-J6" from="J3" to="J6" numLanes="2" speed="13.89"/>
    <edge id="J6-J9" from="J6" to="J9" numLanes="2" speed="13.89"/>
    <edge id="J9-N3" from="J9" to="N3" numLanes="2" speed="13.89"/>
    
    <!-- Reverse vertical -->
    <edge id="J1-S1" from="J1" to="S1" numLanes="2" speed="13.89"/>
    <edge id="J4-J1" from="J4" to="J1" numLanes="2" speed="13.89"/>
    <edge id="J7-J4" from="J7" to="J4" numLanes="2" speed="13.89"/>
    <edge id="N1-J7" from="N1" to="J7" numLanes="2" speed="13.89"/>
</edges>
"""

# Routes
ROUTES = """<?xml version="1.0" encoding="UTF-8"?>
<routes>
    <!-- Vehicle Types -->
    <vType id="car" accel="2.6" decel="4.5" sigma="0.5" length="4.5" maxSpeed="16.67" color="1,1,0"/>
    <vType id="truck" accel="1.3" decel="4.0" sigma="0.5" length="8.0" maxSpeed="11.11" color="0.5,0.5,0.5"/>
    <vType id="ambulance" accel="3.5" decel="5.0" sigma="0.2" length="6.0" maxSpeed="25.0" color="1,0,0" guiShape="emergency"/>
    
    <!-- Routes -->
    <route id="route_h1" edges="W1-J1 J1-J2 J2-J3 J3-E1"/>
    <route id="route_h2" edges="W2-J4 J4-J5 J5-J6 J6-E2"/>
    <route id="route_h3" edges="W3-J7 J7-J8 J8-J9 J9-E3"/>
    <route id="route_v1" edges="S1-J1 J1-J4 J4-J7 J7-N1"/>
    <route id="route_v2" edges="S2-J2 J2-J5 J5-J8 J8-N2"/>
    <route id="route_v3" edges="S3-J3 J3-J6 J6-J9 J9-N3"/>
    
    <!-- Regular traffic flows -->
    <flow id="flow_h1" type="car" route="route_h1" begin="0" end="3600" vehsPerHour="300"/>
    <flow id="flow_h2" type="car" route="route_h2" begin="0" end="3600" vehsPerHour="250"/>
    <flow id="flow_h3" type="car" route="route_h3" begin="0" end="3600" vehsPerHour="200"/>
    <flow id="flow_v1" type="car" route="route_v1" begin="0" end="3600" vehsPerHour="200"/>
    <flow id="flow_v2" type="car" route="route_v2" begin="0" end="3600" vehsPerHour="280"/>
    <flow id="flow_v3" type="car" route="route_v3" begin="0" end="3600" vehsPerHour="180"/>
    
    <!-- Trucks -->
    <flow id="trucks_h1" type="truck" route="route_h1" begin="0" end="3600" vehsPerHour="50"/>
    <flow id="trucks_v2" type="truck" route="route_v2" begin="0" end="3600" vehsPerHour="40"/>
    
    <!-- Emergency vehicles (ambulances) -->
    <vehicle id="AMB001" type="ambulance" route="route_h2" depart="300"/>
    <vehicle id="AMB002" type="ambulance" route="route_v2" depart="600"/>
    <vehicle id="AMB003" type="ambulance" route="route_h1" depart="1200"/>
    <vehicle id="AMB004" type="ambulance" route="route_v1" depart="1800"/>
    
    <!-- Congestion period (rush hour 500-1000) -->
    <flow id="rush_h1" type="car" route="route_h1" begin="500" end="1000" vehsPerHour="600"/>
    <flow id="rush_h2" type="car" route="route_h2" begin="500" end="1000" vehsPerHour="550"/>
    <flow id="rush_v2" type="car" route="route_v2" begin="500" end="1000" vehsPerHour="500"/>
</routes>
"""

# Configuration
CONFIG = """<?xml version="1.0" encoding="UTF-8"?>
<configuration>
    <input>
        <net-file value="grid.net.xml"/>
        <route-files value="grid.rou.xml"/>
    </input>
    <time>
        <begin value="0"/>
        <end value="3600"/>
        <step-length value="0.5"/>
    </time>
    <processing>
        <time-to-teleport value="-1"/>
    </processing>
    <report>
        <verbose value="true"/>
        <no-step-log value="true"/>
    </report>
</configuration>
"""

def main():
    os.makedirs(NETWORK_DIR, exist_ok=True)
    
    # Write node file
    nodes_file = os.path.join(NETWORK_DIR, 'grid.nod.xml')
    with open(nodes_file, 'w') as f:
        f.write(NODES)
    print(f"Created: {nodes_file}")
    
    # Write edge file
    edges_file = os.path.join(NETWORK_DIR, 'grid.edg.xml')
    with open(edges_file, 'w') as f:
        f.write(EDGES)
    print(f"Created: {edges_file}")
    
    # Write routes file
    routes_file = os.path.join(NETWORK_DIR, 'grid.rou.xml')
    with open(routes_file, 'w') as f:
        f.write(ROUTES)
    print(f"Created: {routes_file}")
    
    # Write config file
    config_file = os.path.join(NETWORK_DIR, 'grid.sumocfg')
    with open(config_file, 'w') as f:
        f.write(CONFIG)
    print(f"Created: {config_file}")
    
    # Generate network using netconvert
    net_file = os.path.join(NETWORK_DIR, 'grid.net.xml')
    try:
        cmd = [
            'netconvert',
            '--node-files', nodes_file,
            '--edge-files', edges_file,
            '--output-file', net_file,
            '--tls.guess', 'true'
        ]
        subprocess.run(cmd, check=True, capture_output=True)
        print(f"Created: {net_file}")
        print("\n✅ Network generation complete!")
        print(f"\nTo run simulation: python controller.py -c network/grid.sumocfg --gui")
    except FileNotFoundError:
        print("\n⚠️  netconvert not found. Please install SUMO first.")
        print("   See: https://sumo.dlr.de/docs/Installing/index.html")
        print("\nOnce SUMO is installed, run this script again to generate the network.")
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Error generating network: {e}")
        print(f"stderr: {e.stderr.decode()}")


if __name__ == "__main__":
    main()
