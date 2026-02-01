#!/usr/bin/env python3
"""
Download and setup a realistic city network from OpenStreetMap
Creates a detailed simulation with:
- Real road network
- Realistic traffic lights
- Proper lane markings
- 3D vehicle visualization
"""

import os
import urllib.request
import subprocess
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
NETWORK_DIR = os.path.join(SCRIPT_DIR, 'network', 'realistic')

# Bangalore City Center (MG Road area) - You can change this
# Format: min_lon, min_lat, max_lon, max_lat
LOCATIONS = {
    'bangalore_mg_road': {
        'bbox': (77.5950, 12.9716, 77.6150, 12.9850),
        'name': 'Bangalore MG Road'
    },
    'manhattan': {
        'bbox': (-74.0060, 40.7128, -73.9800, 40.7300),
        'name': 'Manhattan NYC'
    },
    'london': {
        'bbox': (-0.1400, 51.5000, -0.1000, 51.5200),
        'name': 'London City'
    }
}

def download_osm(location_key='bangalore_mg_road'):
    """Download OSM data for specified location"""
    os.makedirs(NETWORK_DIR, exist_ok=True)
    
    loc = LOCATIONS.get(location_key, LOCATIONS['bangalore_mg_road'])
    bbox = loc['bbox']
    
    print(f"📍 Downloading map data for {loc['name']}...")
    
    # Overpass API query
    overpass_url = "https://overpass-api.de/api/map"
    query_url = f"{overpass_url}?bbox={bbox[0]},{bbox[1]},{bbox[2]},{bbox[3]}"
    
    osm_file = os.path.join(NETWORK_DIR, 'city.osm')
    
    try:
        print(f"   Fetching from OpenStreetMap...")
        urllib.request.urlretrieve(query_url, osm_file)
        print(f"   ✓ Downloaded to {osm_file}")
        return osm_file
    except Exception as e:
        print(f"   ❌ Download failed: {e}")
        return None

def convert_to_sumo(osm_file):
    """Convert OSM to SUMO network"""
    net_file = os.path.join(NETWORK_DIR, 'city.net.xml')
    
    print("🔧 Converting to SUMO network...")
    
    cmd = [
        'netconvert',
        '--osm-files', osm_file,
        '--output-file', net_file,
        # Realistic settings
        '--geometry.remove', 'false',
        '--roundabouts.guess', 'true',
        '--ramps.guess', 'true',
        '--junctions.join', 'true',
        '--tls.guess-signals', 'true',
        '--tls.guess', 'true',
        '--tls.default-type', 'actuated',
        # Lane settings
        '--sidewalks.guess', 'true',
        '--crossings.guess', 'true',
        # Output options
        '--output.street-names', 'true',
        '--output.original-names', 'true',
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"   ✓ Network created: {net_file}")
            return net_file
        else:
            print(f"   ⚠️ Warnings during conversion")
            if result.stderr:
                print(f"   {result.stderr[:500]}")
            return net_file
    except Exception as e:
        print(f"   ❌ Conversion failed: {e}")
        return None

def create_vehicle_types():
    """Create realistic vehicle types with 3D models"""
    vtypes_file = os.path.join(NETWORK_DIR, 'vtypes.add.xml')
    
    content = '''<?xml version="1.0" encoding="UTF-8"?>
<additional>
    <!-- Regular Cars -->
    <vType id="car" accel="2.6" decel="4.5" sigma="0.5" length="4.5" maxSpeed="50" 
           color="1,1,0" guiShape="passenger" imgFile=""/>
    <vType id="car_blue" accel="2.6" decel="4.5" sigma="0.5" length="4.5" maxSpeed="50" 
           color="0,0,1" guiShape="passenger"/>
    <vType id="car_red" accel="2.6" decel="4.5" sigma="0.5" length="4.5" maxSpeed="50" 
           color="1,0,0" guiShape="passenger"/>
    <vType id="car_green" accel="2.6" decel="4.5" sigma="0.5" length="4.5" maxSpeed="50" 
           color="0,1,0" guiShape="passenger"/>
    
    <!-- SUVs -->
    <vType id="suv" accel="2.4" decel="4.0" sigma="0.5" length="5.0" width="2.1" maxSpeed="45" 
           color="0.3,0.3,0.3" guiShape="passenger/sedan"/>
    
    <!-- Trucks -->
    <vType id="truck" accel="1.3" decel="4.0" sigma="0.5" length="12.0" width="2.5" maxSpeed="30" 
           color="0.5,0.5,0.5" guiShape="truck"/>
    <vType id="truck_semi" accel="1.0" decel="3.5" sigma="0.5" length="16.0" width="2.5" maxSpeed="25" 
           color="0.4,0.2,0.1" guiShape="truck/semitrailer"/>
    
    <!-- Buses -->
    <vType id="bus" accel="1.2" decel="4.0" sigma="0.5" length="12.0" width="2.55" maxSpeed="25" 
           color="0.1,0.5,0.1" guiShape="bus"/>
    <vType id="bus_city" accel="1.5" decel="4.0" sigma="0.5" length="18.0" width="2.55" maxSpeed="20" 
           color="1,0.5,0" guiShape="bus/flexible"/>
    
    <!-- Motorcycles -->
    <vType id="motorcycle" accel="4.0" decel="6.0" sigma="0.3" length="2.2" width="0.8" maxSpeed="60" 
           color="0.9,0.1,0.1" guiShape="motorcycle"/>
    <vType id="scooter" accel="2.5" decel="5.0" sigma="0.4" length="1.8" width="0.7" maxSpeed="40" 
           color="0.2,0.6,0.8" guiShape="moped"/>
    
    <!-- Bicycles -->
    <vType id="bicycle" accel="1.2" decel="3.0" sigma="0.5" length="1.8" width="0.6" maxSpeed="8" 
           color="0,0.7,0.7" guiShape="bicycle"/>
    
    <!-- Emergency Vehicles -->
    <vType id="ambulance" accel="3.5" decel="5.0" sigma="0.2" length="6.5" width="2.2" maxSpeed="70" 
           color="1,1,1" guiShape="emergency" 
           emergencyDecel="9.0" speedDev="0.1"/>
    <vType id="fire_truck" accel="2.0" decel="4.5" sigma="0.2" length="10.0" width="2.5" maxSpeed="60" 
           color="1,0,0" guiShape="firebrigade"/>
    <vType id="police" accel="4.0" decel="6.0" sigma="0.1" length="5.0" width="2.0" maxSpeed="80" 
           color="0,0,0.8" guiShape="emergency"/>
    
    <!-- Auto-rickshaws (common in India) -->
    <vType id="auto" accel="2.0" decel="4.0" sigma="0.6" length="2.7" width="1.4" maxSpeed="25" 
           color="0,0.8,0" guiShape="passenger/hatchback"/>
    
    <!-- Pedestrians -->
    <vType id="pedestrian" vClass="pedestrian" guiShape="pedestrian" width="0.5" length="0.3" 
           minGap="0.25" maxSpeed="1.5" color="0.9,0.7,0.5"/>
</additional>
'''
    
    with open(vtypes_file, 'w') as f:
        f.write(content)
    
    print(f"   ✓ Vehicle types created: {vtypes_file}")
    return vtypes_file

def create_routes(net_file):
    """Generate random routes using randomTrips.py"""
    route_file = os.path.join(NETWORK_DIR, 'routes.rou.xml')
    
    print("🚗 Generating traffic routes...")
    
    # Use SUMO's randomTrips.py
    random_trips = '/usr/share/sumo/tools/randomTrips.py'
    
    if not os.path.exists(random_trips):
        print(f"   ⚠️ randomTrips.py not found, creating manual routes")
        create_manual_routes(net_file, route_file)
        return route_file
    
    try:
        # Generate trips for different vehicle types
        cmd = [
            sys.executable, random_trips,
            '-n', net_file,
            '-o', os.path.join(NETWORK_DIR, 'trips.trips.xml'),
            '-r', route_file,
            '--begin', '0',
            '--end', '3600',
            '--period', '1',  # One vehicle per second
            '--validate',
            '--vehicle-class', 'passenger',
        ]
        
        subprocess.run(cmd, capture_output=True, check=True)
        print(f"   ✓ Routes created: {route_file}")
        return route_file
    except Exception as e:
        print(f"   ⚠️ Auto-generation failed, creating manual routes")
        create_manual_routes(net_file, route_file)
        return route_file

def create_manual_routes(net_file, route_file):
    """Create manual route file as fallback"""
    content = '''<?xml version="1.0" encoding="UTF-8"?>
<routes>
    <!-- Traffic will be generated by SUMO's traffic demand tools -->
</routes>
'''
    with open(route_file, 'w') as f:
        f.write(content)

def create_gui_settings():
    """Create enhanced GUI settings for 3D visualization"""
    gui_file = os.path.join(NETWORK_DIR, 'gui-settings.xml')
    
    content = '''<?xml version="1.0" encoding="UTF-8"?>
<viewsettings>
    <scheme name="D.R.I.V.E Realistic">
        <!-- Dark background for better contrast -->
        <background backgroundColor="0.1,0.1,0.15" showGrid="false"/>
        
        <!-- Edges (Roads) Settings -->
        <edges laneEdgeMode="0" scaleMode="0" 
               laneShowBorders="true" showLinkDecals="true" 
               showLinkRules="true" showRails="true"
               edgeName_show="false" edgeName_size="50"
               streetName_show="true" streetName_size="55">
            <colorScheme name="by speed (lanewise)">
                <entry color="red" threshold="0"/>
                <entry color="orange" threshold="5"/>
                <entry color="yellow" threshold="10"/>
                <entry color="green" threshold="15"/>
                <entry color="cyan" threshold="20"/>
            </colorScheme>
        </edges>
        
        <!-- Vehicle Settings -->
        <vehicles vehicleMode="9" vehicleQuality="3" 
                  minVehicleSize="1" vehicleExaggeration="1"
                  showBlinker="true" drawMinGap="false"
                  vehicleName_show="false" vehicleName_size="50">
            <colorScheme name="by speed">
                <entry color="red" threshold="0"/>
                <entry color="orange" threshold="10"/>
                <entry color="yellow" threshold="20"/>
                <entry color="green" threshold="30"/>
                <entry color="cyan" threshold="40"/>
                <entry color="blue" threshold="50"/>
            </colorScheme>
        </vehicles>
        
        <!-- Junction Settings -->
        <junctions junctionMode="0" drawLinkTLIndex="false" 
                   drawLinkJunctionIndex="false" 
                   junctionName_show="false" junctionName_size="50"
                   internalJunctionName_show="false">
        </junctions>
        
        <!-- Persons/Pedestrians -->
        <persons personMode="0" personQuality="2" 
                 personExaggeration="1" personName_show="false">
        </persons>
        
        <!-- Additional visualization -->
        <additionals addMode="0" addSize="1" addName_show="false"/>
        
        <!-- POIs -->
        <pois poiSize="0" poiName_show="false"/>
        
        <!-- Polygons (buildings) -->
        <polys polySize="0" polyName_show="false"/>
        
        <!-- 3D Settings -->
        <opengl dither="true" fps="true" 
                drawBoundaries="false" forceDrawForPositionSelection="false"/>
        
        <!-- Legend -->
        <legend showSizeLegend="true" showColorLegend="true"/>
    </scheme>
    
    <!-- Default view settings -->
    <delay value="50"/>
    <viewport zoom="500" x="0" y="0" angle="0"/>
    <decals>
        <!-- Enable decals for realistic road markings -->
    </decals>
    
    <!-- Breakpoints for debugging -->
    <breakpoints-file value=""/>
</viewsettings>
'''
    
    with open(gui_file, 'w') as f:
        f.write(content)
    
    print(f"   ✓ GUI settings created: {gui_file}")
    return gui_file

def create_sumo_config(net_file, route_file, vtypes_file, gui_file):
    """Create SUMO configuration file"""
    config_file = os.path.join(NETWORK_DIR, 'city.sumocfg')
    
    content = f'''<?xml version="1.0" encoding="UTF-8"?>
<configuration>
    <input>
        <net-file value="city.net.xml"/>
        <route-files value="routes.rou.xml"/>
        <additional-files value="vtypes.add.xml"/>
        <gui-settings-file value="gui-settings.xml"/>
    </input>
    
    <time>
        <begin value="0"/>
        <end value="7200"/>
        <step-length value="0.1"/>
    </time>
    
    <processing>
        <time-to-teleport value="-1"/>
        <collision.action value="warn"/>
        <collision.check-junctions value="true"/>
        <pedestrian.model value="striping"/>
        <pedestrian.striping.stripe-width value="0.55"/>
    </processing>
    
    <routing>
        <device.rerouting.probability value="0.7"/>
        <device.rerouting.period value="300"/>
    </routing>
    
    <report>
        <verbose value="true"/>
        <no-step-log value="false"/>
        <duration-log.statistics value="true"/>
        <statistic-output value="stats.xml"/>
    </report>
    
    <gui_only>
        <gui-settings-file value="gui-settings.xml"/>
        <start value="true"/>
        <quit-on-end value="false"/>
        <tracker-interval value="1"/>
        <window-pos value="50,50"/>
        <window-size value="1600,900"/>
    </gui_only>
</configuration>
'''
    
    with open(config_file, 'w') as f:
        f.write(content)
    
    print(f"   ✓ SUMO config created: {config_file}")
    return config_file

def main():
    print("=" * 60)
    print("🌍 D.R.I.V.E - Realistic City Simulation Setup")
    print("=" * 60)
    print()
    
    # Get location choice
    print("Available locations:")
    for i, (key, loc) in enumerate(LOCATIONS.items(), 1):
        print(f"  {i}. {loc['name']} ({key})")
    
    choice = input("\nSelect location (1-3) or press Enter for Bangalore: ").strip()
    
    if choice == '2':
        location_key = 'manhattan'
    elif choice == '3':
        location_key = 'london'
    else:
        location_key = 'bangalore_mg_road'
    
    print()
    
    # Download OSM data
    osm_file = download_osm(location_key)
    if not osm_file:
        print("❌ Failed to download map data")
        return
    
    # Convert to SUMO network
    net_file = convert_to_sumo(osm_file)
    if not net_file:
        print("❌ Failed to convert network")
        return
    
    # Create vehicle types
    vtypes_file = create_vehicle_types()
    
    # Create routes
    route_file = create_routes(net_file)
    
    # Create GUI settings
    gui_file = create_gui_settings()
    
    # Create SUMO config
    config_file = create_sumo_config(net_file, route_file, vtypes_file, gui_file)
    
    print()
    print("=" * 60)
    print("✅ Realistic simulation setup complete!")
    print("=" * 60)
    print()
    print(f"📂 Files created in: {NETWORK_DIR}")
    print()
    print("To run the simulation:")
    print(f"  cd simulation")
    print(f"  sumo-gui -c network/realistic/city.sumocfg")
    print()
    print("Or with the controller:")
    print(f"  python controller.py -c network/realistic/city.sumocfg --gui")
    print()

if __name__ == "__main__":
    main()
