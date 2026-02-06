
import os
import sys
import subprocess
import urllib.request

# Configuration
SUMO_HOME = os.environ.get("SUMO_HOME", "/usr/share/sumo")
TOOLS_DIR = os.path.join(SUMO_HOME, "tools")
sys.path.append(TOOLS_DIR)

NETWORK_DIR = "network"
OSM_FILE = os.path.join(NETWORK_DIR, "bangalore.osm")
NET_FILE = os.path.join(NETWORK_DIR, "bangalore.net.xml")
ROU_FILE = os.path.join(NETWORK_DIR, "bangalore.rou.xml")
CFG_FILE = os.path.join(NETWORK_DIR, "bangalore.sumocfg")
POLY_FILE = os.path.join(NETWORK_DIR, "bangalore.poly.xml")

# Bangalore Coordinates (MG Road / Central Area)
# min_lon, min_lat, max_lon, max_lat
BBOX = "77.590,12.970,77.610,12.985"
OVERPASS_URL = f"https://overpass-api.de/api/map?bbox={BBOX}"

def check_sumo_tools():
    if not os.path.exists(TOOLS_DIR):
        print(f"Error: SUMO tools not found at {TOOLS_DIR}")
        sys.exit(1)
    print(f"SUMO tools found at {TOOLS_DIR}")

def download_osm():
    if os.path.exists(OSM_FILE) and os.path.getsize(OSM_FILE) > 0:
        print(f"OSM file {OSM_FILE} already exists. Skipping download.")
        return

    print(f"Downloading Bangalore map data (bbox={BBOX})...")
    if not os.path.exists(NETWORK_DIR):
        os.makedirs(NETWORK_DIR)
    
    try:
        urllib.request.urlretrieve(OVERPASS_URL, OSM_FILE)
        print(f"Downloaded OSM data to {OSM_FILE}")
    except Exception as e:
        print(f"Failed to download map: {e}")
        sys.exit(1)

def convert_net():
    print("Converting OSM to SUMO network...")
    cmd = [
        "netconvert",
        "--osm-files", OSM_FILE,
        "--output-file", NET_FILE,
        "--geometry.remove", "true",
        "--roundabouts.guess", "true",
        "--ramps.guess", "true",
        "--junctions.join", "true",
        "--tls.guess", "true",
        "--tls.join", "true",
        "--default.lanenumber", "2"
    ]
    subprocess.run(cmd, check=True)
    print(f"Created network file {NET_FILE}")

def generate_traffic():
    print("Generating random traffic demand...")
    random_trips_script = os.path.join(TOOLS_DIR, "randomTrips.py")
    
    cmd = [
        "python3", random_trips_script,
        "-n", NET_FILE,
        "-r", ROU_FILE,
        "-e", "3600",  # 1 hour simulation
        "-p", "2.0",   # A vehicle every 2 seconds
        "--trip-attributes", 'departLane="best" departSpeed="max" departPos="random"',
        "--validate"
    ]
    subprocess.run(cmd, check=True)
    print(f"Created routes file {ROU_FILE}")

def import_polygons():
    print("Importing polygons (buildings, water)...")
    cmd = [
        "polyconvert",
        "--net-file", NET_FILE,
        "--osm-files", OSM_FILE,
        "--output-file", POLY_FILE,
        "--type-file", os.path.join(SUMO_HOME, "data/typemap/osmPolyconvert.typ.xml")
    ]
    try:
        subprocess.run(cmd, check=True)
        print(f"Created polygons file {POLY_FILE}")
    except Exception as e:
        print(f"Warning: Failed to create polygons (might be missing config): {e}")
        # Create empty poly file to prevent errors
        with open(POLY_FILE, 'w') as f:
            f.write('<additional></additional>')

def create_config():
    print("Creating SUMO config file...")
    config_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<configuration xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="http://sumo.dlr.de/xsd/sumoConfiguration.xsd">
    <input>
        <net-file value="bangalore.net.xml"/>
        <route-files value="bangalore.rou.xml"/>
        <additional-files value="bangalore.poly.xml"/>
    </input>
    <time>
        <begin value="0"/>
        <end value="3600"/>
    </time>
    <processing>
        <ignore-route-errors value="true"/>
    </processing>
    <report>
        <verbose value="true"/>
        <duration-log.statistics value="true"/>
        <no-step-log value="true"/>
    </report>
</configuration>
"""
    with open(CFG_FILE, "w") as f:
        f.write(config_content)
    print(f"Created config file {CFG_FILE}")

def main():
    check_sumo_tools()
    download_osm()
    convert_net()
    import_polygons() # Try to import polygons for better visuals
    generate_traffic()
    create_config()
    print("\nSetup complete! You can run the simulation with:")
    print("python3 controller.py --config network/bangalore.sumocfg --gui")

if __name__ == "__main__":
    main()
