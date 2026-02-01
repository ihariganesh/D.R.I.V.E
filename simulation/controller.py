"""
SUMO Traffic Controller - Core A
Manages SUMO simulation with dynamic speed limits and Green Wave protocol

Features:
- Dynamic speed limit adjustment based on traffic density
- Green Wave protocol for emergency vehicles (ambulances)
- Real-time traffic metrics reporting
- Integration with D.R.I.V.E dashboard via API
"""

import os
import sys
import time
import json
import argparse
import logging
import sqlite3
import requests
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from threading import Thread
from dataclasses import dataclass, asdict

# SUMO configuration
if 'SUMO_HOME' in os.environ:
    tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
    sys.path.append(tools)
else:
    sys.exit("Please set SUMO_HOME environment variable")

import traci
import sumolib

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class TrafficMetrics:
    """Traffic metrics for a specific edge"""
    edge_id: str
    vehicle_count: int
    average_speed: float  # m/s
    density: float  # vehicles per km
    occupancy: float  # percentage
    waiting_time: float  # seconds
    timestamp: str


@dataclass
class SimulationState:
    """Current state of the simulation"""
    step: int
    time: float
    total_vehicles: int
    average_speed: float
    total_waiting_time: float
    ambulances_active: int
    green_wave_active: bool
    speed_limits_modified: List[str]


class SUMOController:
    """
    SUMO Traffic Controller with AI-powered features
    
    Implements:
    1. Dynamic speed limits based on traffic density
    2. Green Wave protocol for emergency vehicles
    3. Real-time metrics collection and reporting
    """
    
    # Configuration constants
    DENSITY_THRESHOLD = 30  # vehicles per edge to trigger speed reduction
    LOW_SPEED_LIMIT = 30 / 3.6  # 30 km/h in m/s
    NORMAL_SPEED_LIMIT = 50 / 3.6  # 50 km/h in m/s
    GREEN_WAVE_ADVANCE_TIME = 45  # seconds ahead to turn lights green
    
    def __init__(
        self,
        sumo_config: str,
        use_gui: bool = True,
        step_length: float = 0.1,
        api_url: Optional[str] = None,
        db_path: str = "simulation_logs.db"
    ):
        """
        Initialize SUMO controller
        
        Args:
            sumo_config: Path to SUMO configuration file (.sumocfg)
            use_gui: Whether to use SUMO-GUI (True) or command line (False)
            step_length: Simulation step length in seconds
            api_url: Optional URL for D.R.I.V.E API to send metrics
            db_path: Path to SQLite database for logging
        """
        self.sumo_config = sumo_config
        self.use_gui = use_gui
        self.step_length = step_length
        self.api_url = api_url
        self.db_path = db_path
        
        # State tracking
        self.modified_edges: Dict[str, float] = {}  # edge_id -> original speed limit
        self.active_green_waves: Dict[str, dict] = {}  # vehicle_id -> green wave data
        self.metrics_history: List[TrafficMetrics] = []
        self.running = False
        self.current_step = 0
        
        # Initialize database
        self._init_database()
    
    def _init_database(self):
        """Initialize SQLite database for logging"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create metrics table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS traffic_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                edge_id TEXT NOT NULL,
                vehicle_count INTEGER,
                average_speed REAL,
                density REAL,
                occupancy REAL,
                waiting_time REAL
            )
        ''')
        
        # Create events table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS simulation_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                event_type TEXT NOT NULL,
                entity_id TEXT,
                details TEXT
            )
        ''')
        
        # Create green wave sessions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS green_wave_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                vehicle_id TEXT NOT NULL,
                vehicle_type TEXT,
                start_time TEXT,
                end_time TEXT,
                affected_lights TEXT,
                status TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
        logger.info(f"Database initialized at {self.db_path}")
    
    def start(self):
        """Start SUMO simulation"""
        logger.info("Starting SUMO simulation...")
        
        # Build SUMO command
        sumo_binary = "sumo-gui" if self.use_gui else "sumo"
        sumo_cmd = [
            sumo_binary,
            "-c", self.sumo_config,
            "--step-length", str(self.step_length),
            "--waiting-time-memory", "1000",
            "--collision.action", "remove",
        ]
        
        # Start SUMO
        traci.start(sumo_cmd)
        self.running = True
        
        # Log event
        self._log_event("simulation_start", None, {"config": self.sumo_config})
        
        logger.info("SUMO simulation started successfully")
    
    def stop(self):
        """Stop SUMO simulation"""
        logger.info("Stopping SUMO simulation...")
        self.running = False
        
        # Restore all modified speed limits
        self._restore_all_speed_limits()
        
        # Close SUMO
        traci.close()
        
        # Log event
        self._log_event("simulation_stop", None, {"total_steps": self.current_step})
        
        logger.info("SUMO simulation stopped")
    
    def run(self, max_steps: Optional[int] = None):
        """
        Run simulation loop
        
        Args:
            max_steps: Maximum steps to run (None for infinite)
        """
        self.start()
        
        try:
            while self.running:
                # Check max steps
                if max_steps and self.current_step >= max_steps:
                    logger.info(f"Reached max steps: {max_steps}")
                    break
                
                # Perform simulation step
                self._simulation_step()
                self.current_step += 1
                
                # Check if simulation ended
                if traci.simulation.getMinExpectedNumber() <= 0:
                    logger.info("All vehicles have completed their routes")
                    break
                    
        except KeyboardInterrupt:
            logger.info("Simulation interrupted by user")
        except Exception as e:
            logger.error(f"Simulation error: {e}")
            raise
        finally:
            self.stop()
    
    def _simulation_step(self):
        """Execute a single simulation step"""
        # Advance simulation
        traci.simulationStep()
        
        # Get all edges
        edges = traci.edge.getIDList()
        
        # Process each edge for traffic density
        for edge_id in edges:
            if edge_id.startswith(":"):  # Skip internal edges
                continue
            
            # Calculate density
            vehicle_count = traci.edge.getLastStepVehicleNumber(edge_id)
            
            # Apply dynamic speed limit
            self._apply_dynamic_speed_limit(edge_id, vehicle_count)
        
        # Check for ambulances and apply Green Wave
        self._process_emergency_vehicles()
        
        # Collect and report metrics periodically (every 100 steps)
        if self.current_step % 100 == 0:
            self._collect_and_report_metrics(edges)
    
    def _apply_dynamic_speed_limit(self, edge_id: str, vehicle_count: int):
        """
        Apply dynamic speed limit based on traffic density
        
        Logic:
        - If density > DENSITY_THRESHOLD: reduce speed to LOW_SPEED_LIMIT
        - If density drops below threshold: restore original speed
        """
        if vehicle_count > self.DENSITY_THRESHOLD:
            # High density - reduce speed limit
            if edge_id not in self.modified_edges:
                # Store original limit and reduce
                original_limit = traci.edge.getMaxSpeed(edge_id)
                self.modified_edges[edge_id] = original_limit
                
                traci.edge.setMaxSpeed(edge_id, self.LOW_SPEED_LIMIT)
                
                logger.info(
                    f"Speed limit reduced on {edge_id}: "
                    f"{original_limit*3.6:.1f} -> {self.LOW_SPEED_LIMIT*3.6:.1f} km/h "
                    f"(density: {vehicle_count} vehicles)"
                )
                
                self._log_event(
                    "speed_limit_reduced",
                    edge_id,
                    {
                        "original_limit": original_limit * 3.6,
                        "new_limit": self.LOW_SPEED_LIMIT * 3.6,
                        "vehicle_count": vehicle_count
                    }
                )
        else:
            # Low density - restore original speed if modified
            if edge_id in self.modified_edges:
                original_limit = self.modified_edges.pop(edge_id)
                traci.edge.setMaxSpeed(edge_id, original_limit)
                
                logger.info(
                    f"Speed limit restored on {edge_id}: "
                    f"{self.LOW_SPEED_LIMIT*3.6:.1f} -> {original_limit*3.6:.1f} km/h"
                )
                
                self._log_event(
                    "speed_limit_restored",
                    edge_id,
                    {"restored_limit": original_limit * 3.6}
                )
    
    def _process_emergency_vehicles(self):
        """
        Process emergency vehicles and apply Green Wave protocol
        
        Green Wave Logic:
        1. Detect ambulances in the simulation
        2. Get their current lane/edge
        3. Find traffic lights on their path
        4. Force green phase for approaching traffic lights
        """
        # Get all vehicles
        vehicle_ids = traci.vehicle.getIDList()
        
        for vehicle_id in vehicle_ids:
            # Check if vehicle is an ambulance
            vehicle_type = traci.vehicle.getTypeID(vehicle_id)
            
            if vehicle_type.lower() in ["ambulance", "emergency", "fire_truck", "police"]:
                # Get vehicle position and lane
                lane_id = traci.vehicle.getLaneID(vehicle_id)
                edge_id = traci.lane.getEdgeID(lane_id)
                position = traci.vehicle.getPosition(vehicle_id)
                speed = traci.vehicle.getSpeed(vehicle_id)
                
                # Find nearby traffic lights
                self._apply_green_wave(vehicle_id, vehicle_type, edge_id, position, speed)
    
    def _apply_green_wave(
        self,
        vehicle_id: str,
        vehicle_type: str,
        edge_id: str,
        position: Tuple[float, float],
        speed: float
    ):
        """
        Apply Green Wave protocol for emergency vehicle
        
        Args:
            vehicle_id: Emergency vehicle ID
            vehicle_type: Type of emergency vehicle
            edge_id: Current edge the vehicle is on
            position: Current (x, y) position
            speed: Current speed in m/s
        """
        # Get all traffic lights
        traffic_light_ids = traci.trafficlight.getIDList()
        
        for tl_id in traffic_light_ids:
            # Get traffic light position (approximate)
            # In real implementation, get from network file
            controlled_lanes = traci.trafficlight.getControlledLanes(tl_id)
            
            # Check if any controlled lane is on the ambulance's edge
            for lane in controlled_lanes:
                lane_edge = traci.lane.getEdgeID(lane)
                
                if lane_edge == edge_id:
                    # Ambulance is approaching this traffic light
                    # Calculate time to reach
                    distance = traci.vehicle.getDrivingDistance(vehicle_id, lane, 0)
                    
                    if 0 < distance < (speed * self.GREEN_WAVE_ADVANCE_TIME):
                        # Vehicle will reach in ADVANCE_TIME seconds - activate green
                        self._force_green_phase(tl_id, vehicle_id)
                        break
    
    def _force_green_phase(self, traffic_light_id: str, vehicle_id: str):
        """
        Force traffic light to green phase for emergency vehicle
        
        Args:
            traffic_light_id: Traffic light ID to control
            vehicle_id: Emergency vehicle ID (for logging)
        """
        # Get current phase
        current_phase = traci.trafficlight.getPhase(traffic_light_id)
        current_program = traci.trafficlight.getProgram(traffic_light_id)
        
        # Get all phases
        logic = traci.trafficlight.getAllProgramLogics(traffic_light_id)[0]
        phases = logic.getPhases()
        
        # Find green phase for the main direction (usually phase 0 or phase with most 'G')
        green_phase_index = 0
        max_green = 0
        
        for i, phase in enumerate(phases):
            green_count = phase.state.count('G') + phase.state.count('g')
            if green_count > max_green:
                max_green = green_count
                green_phase_index = i
        
        # Set to green phase if not already
        if current_phase != green_phase_index:
            traci.trafficlight.setPhase(traffic_light_id, green_phase_index)
            
            # Track active green wave
            wave_key = f"{vehicle_id}_{traffic_light_id}"
            if wave_key not in self.active_green_waves:
                self.active_green_waves[wave_key] = {
                    "vehicle_id": vehicle_id,
                    "traffic_light_id": traffic_light_id,
                    "activated_at": self.current_step,
                    "original_phase": current_phase
                }
                
                logger.info(
                    f"GREEN WAVE ACTIVATED: Traffic light {traffic_light_id} "
                    f"set to green for {vehicle_id}"
                )
                
                self._log_event(
                    "green_wave_activated",
                    traffic_light_id,
                    {
                        "vehicle_id": vehicle_id,
                        "original_phase": current_phase,
                        "new_phase": green_phase_index
                    }
                )
    
    def _restore_all_speed_limits(self):
        """Restore all modified speed limits to original values"""
        for edge_id, original_limit in self.modified_edges.items():
            try:
                traci.edge.setMaxSpeed(edge_id, original_limit)
                logger.info(f"Restored speed limit on {edge_id}")
            except Exception as e:
                logger.warning(f"Could not restore speed limit on {edge_id}: {e}")
        
        self.modified_edges.clear()
    
    def _collect_and_report_metrics(self, edges: List[str]):
        """Collect traffic metrics and report to dashboard"""
        total_vehicles = 0
        total_speed = 0
        total_waiting_time = 0
        edge_count = 0
        
        for edge_id in edges:
            if edge_id.startswith(":"):
                continue
            
            try:
                vehicle_count = traci.edge.getLastStepVehicleNumber(edge_id)
                mean_speed = traci.edge.getLastStepMeanSpeed(edge_id)
                occupancy = traci.edge.getLastStepOccupancy(edge_id)
                waiting_time = traci.edge.getWaitingTime(edge_id)
                
                # Calculate density (vehicles per km)
                edge_length = traci.lane.getLength(f"{edge_id}_0")
                density = (vehicle_count / edge_length) * 1000 if edge_length > 0 else 0
                
                # Create metrics object
                metrics = TrafficMetrics(
                    edge_id=edge_id,
                    vehicle_count=vehicle_count,
                    average_speed=mean_speed,
                    density=density,
                    occupancy=occupancy,
                    waiting_time=waiting_time,
                    timestamp=datetime.now().isoformat()
                )
                
                # Save to database
                self._save_metrics(metrics)
                
                # Accumulate totals
                total_vehicles += vehicle_count
                if mean_speed > 0:
                    total_speed += mean_speed
                    edge_count += 1
                total_waiting_time += waiting_time
                
            except Exception as e:
                logger.debug(f"Could not get metrics for edge {edge_id}: {e}")
        
        # Calculate averages
        avg_speed = (total_speed / edge_count) if edge_count > 0 else 0
        
        # Create simulation state
        state = SimulationState(
            step=self.current_step,
            time=traci.simulation.getTime(),
            total_vehicles=total_vehicles,
            average_speed=avg_speed * 3.6,  # Convert to km/h
            total_waiting_time=total_waiting_time,
            ambulances_active=len(self.active_green_waves),
            green_wave_active=len(self.active_green_waves) > 0,
            speed_limits_modified=list(self.modified_edges.keys())
        )
        
        logger.info(
            f"Step {self.current_step}: {total_vehicles} vehicles, "
            f"avg speed: {avg_speed*3.6:.1f} km/h, "
            f"green waves: {len(self.active_green_waves)}"
        )
        
        # Send to API if configured
        if self.api_url:
            self._send_to_api(state)
    
    def _save_metrics(self, metrics: TrafficMetrics):
        """Save metrics to SQLite database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO traffic_metrics 
                (timestamp, edge_id, vehicle_count, average_speed, density, occupancy, waiting_time)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                metrics.timestamp,
                metrics.edge_id,
                metrics.vehicle_count,
                metrics.average_speed,
                metrics.density,
                metrics.occupancy,
                metrics.waiting_time
            ))
            
            conn.commit()
            conn.close()
        except Exception as e:
            logger.warning(f"Could not save metrics: {e}")
    
    def _log_event(self, event_type: str, entity_id: Optional[str], details: dict):
        """Log simulation event to database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO simulation_events (timestamp, event_type, entity_id, details)
                VALUES (?, ?, ?, ?)
            ''', (
                datetime.now().isoformat(),
                event_type,
                entity_id,
                json.dumps(details)
            ))
            
            conn.commit()
            conn.close()
        except Exception as e:
            logger.warning(f"Could not log event: {e}")
    
    def _send_to_api(self, state: SimulationState):
        """Send simulation state to D.R.I.V.E API"""
        if not self.api_url:
            return
        
        try:
            response = requests.post(
                f"{self.api_url}/api/v1/simulation/metrics",
                json=asdict(state),
                timeout=5
            )
            if response.status_code != 200:
                logger.warning(f"API returned status {response.status_code}")
        except Exception as e:
            logger.debug(f"Could not send to API: {e}")
    
    # --- External Control Methods (for Dashboard) ---
    
    def force_red_light(self, traffic_light_id: str, duration_seconds: int = 30):
        """
        Force a traffic light to red (all directions)
        
        Args:
            traffic_light_id: Traffic light ID
            duration_seconds: How long to keep it red
        """
        try:
            # Get current state length
            logic = traci.trafficlight.getAllProgramLogics(traffic_light_id)[0]
            phases = logic.getPhases()
            
            # Find or create all-red phase
            red_state = 'r' * len(phases[0].state)
            
            # Set to red
            traci.trafficlight.setRedYellowGreenState(traffic_light_id, red_state)
            
            logger.info(f"MANUAL OVERRIDE: Traffic light {traffic_light_id} set to RED")
            
            self._log_event(
                "manual_red_light",
                traffic_light_id,
                {"duration": duration_seconds}
            )
            
            return True
        except Exception as e:
            logger.error(f"Could not force red light: {e}")
            return False
    
    def set_speed_limit(self, edge_id: str, speed_kmh: float):
        """
        Manually set speed limit on an edge
        
        Args:
            edge_id: Edge ID
            speed_kmh: Speed limit in km/h
        """
        try:
            speed_ms = speed_kmh / 3.6
            traci.edge.setMaxSpeed(edge_id, speed_ms)
            
            logger.info(f"MANUAL OVERRIDE: Speed limit on {edge_id} set to {speed_kmh} km/h")
            
            self._log_event(
                "manual_speed_limit",
                edge_id,
                {"speed_kmh": speed_kmh}
            )
            
            return True
        except Exception as e:
            logger.error(f"Could not set speed limit: {e}")
            return False
    
    def get_current_state(self) -> dict:
        """Get current simulation state for dashboard"""
        try:
            total_vehicles = traci.vehicle.getIDCount()
            
            # Calculate average speed
            speeds = [traci.vehicle.getSpeed(v) for v in traci.vehicle.getIDList()]
            avg_speed = sum(speeds) / len(speeds) if speeds else 0
            
            return {
                "step": self.current_step,
                "time": traci.simulation.getTime(),
                "total_vehicles": total_vehicles,
                "average_speed_kmh": avg_speed * 3.6,
                "modified_edges": list(self.modified_edges.keys()),
                "active_green_waves": len(self.active_green_waves),
                "running": self.running
            }
        except Exception as e:
            logger.error(f"Could not get state: {e}")
            return {}


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='SUMO Traffic Controller')
    parser.add_argument(
        '-c', '--config',
        default='network/city.sumocfg',
        help='Path to SUMO configuration file'
    )
    parser.add_argument(
        '--gui',
        action='store_true',
        help='Use SUMO-GUI'
    )
    parser.add_argument(
        '--nogui',
        action='store_true',
        help='Run without GUI'
    )
    parser.add_argument(
        '--steps',
        type=int,
        default=None,
        help='Maximum simulation steps'
    )
    parser.add_argument(
        '--api-url',
        default=None,
        help='D.R.I.V.E API URL for metrics reporting'
    )
    parser.add_argument(
        '--scenario',
        choices=['normal', 'congestion', 'emergency'],
        default='normal',
        help='Scenario to run'
    )
    
    args = parser.parse_args()
    
    # Determine GUI usage
    use_gui = not args.nogui if args.nogui else args.gui
    
    # Get config path
    script_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(script_dir, args.config)
    
    if not os.path.exists(config_path):
        logger.error(f"Configuration file not found: {config_path}")
        logger.info("Please create SUMO network files in the 'network' directory")
        logger.info("See README.md for instructions")
        sys.exit(1)
    
    # Create and run controller
    controller = SUMOController(
        sumo_config=config_path,
        use_gui=use_gui,
        api_url=args.api_url
    )
    
    controller.run(max_steps=args.steps)


if __name__ == "__main__":
    main()
