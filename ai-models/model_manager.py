"""
AI Model Manager
Central integration point for all AI models in D.R.I.V.E system
"""
import sys
import os
from pathlib import Path

# Add ai-models to path
sys.path.insert(0, str(Path(__file__).parent))

from typing import Dict, List, Optional
import numpy as np

# Import all AI models
from event_detection.event_detector import EventDetector
from speed_optimization.speed_optimizer import SpeedOptimizer
from traffic_flow.density_estimator import TrafficDensityEstimator
from digital_twin.simulator import DigitalTwinSimulator
from green_wave.controller import GreenWaveController


class AIModelManager:
    """
    Central manager for all AI models
    Provides unified interface for backend services
    """
    
    def __init__(self, config: Optional[Dict] = None):
        """
        Initialize all AI models
        
        Args:
            config: Configuration dictionary for models
        """
        self.config = config or {}
        
        # Initialize models
        print("🤖 Initializing AI models...")
        
        try:
            self.event_detector = EventDetector()
            print("  ✓ Event Detector loaded")
        except Exception as e:
            print(f"  ✗ Event Detector failed: {e}")
            self.event_detector = None
        
        try:
            self.speed_optimizer = SpeedOptimizer()
            print("  ✓ Speed Optimizer loaded")
        except Exception as e:
            print(f"  ✗ Speed Optimizer failed: {e}")
            self.speed_optimizer = None
        
        try:
            yolo_path = self.config.get("yolo_model_path", "yolov8n.pt")
            self.density_estimator = TrafficDensityEstimator(yolo_path)
            print("  ✓ Traffic Density Estimator loaded")
        except Exception as e:
            print(f"  ✗ Traffic Density Estimator failed: {e}")
            self.density_estimator = None
        
        try:
            sim_duration = self.config.get("simulation_duration", 5)
            self.digital_twin = DigitalTwinSimulator(sim_duration)
            print("  ✓ Digital Twin Simulator loaded")
        except Exception as e:
            print(f"  ✗ Digital Twin Simulator failed: {e}")
            self.digital_twin = None
        
        try:
            advance_time = self.config.get("green_wave_advance_time", 45)
            self.green_wave = GreenWaveController(advance_time)
            print("  ✓ Green Wave Controller loaded")
        except Exception as e:
            print(f"  ✗ Green Wave Controller failed: {e}")
            self.green_wave = None
        
        print("✅ AI Model Manager initialized\n")
    
    # Traffic Flow Analysis
    def analyze_traffic(self, frame: np.ndarray) -> Dict:
        """Analyze traffic from camera frame"""
        if not self.density_estimator:
            return {"error": "Density estimator not available"}
        
        return self.density_estimator.process_frame(frame)
    
    # Event Detection
    def detect_events(
        self,
        frame: np.ndarray,
        vehicle_positions: List,
        vehicle_count: int,
        avg_speed: float
    ) -> List[Dict]:
        """Detect traffic events"""
        if not self.event_detector:
            return []
        
        events = []
        
        # Check for accidents
        accident = self.event_detector.detect_accident(frame, vehicle_positions)
        if accident.get("detected"):
            events.append(accident)
        
        # Check for congestion
        congestion = self.event_detector.detect_congestion(vehicle_count, avg_speed)
        if congestion.get("detected"):
            events.append(congestion)
        
        # Check for debris
        debris = self.event_detector.detect_debris(frame)
        if debris.get("detected"):
            events.append(debris)
        
        return events
    
    # Speed Optimization
    def optimize_speed(
        self,
        current_speed: int,
        vehicle_count: int,
        avg_speed: float,
        congestion_level: float,
        events: List[Dict],
        weather: str = "clear"
    ) -> Dict:
        """Calculate optimal speed limit with XAI explanation"""
        if not self.speed_optimizer:
            return {"error": "Speed optimizer not available"}
        
        return self.speed_optimizer.calculate_optimal_speed(
            current_speed, vehicle_count, avg_speed,
            congestion_level, events, weather
        )
    
    # Digital Twin Simulation
    def simulate_override(
        self,
        current_state: Dict,
        proposed_changes: Dict
    ) -> Dict:
        """Simulate impact of manual override"""
        if not self.digital_twin:
            return {"error": "Digital twin not available"}
        
        return self.digital_twin.simulate_override(current_state, proposed_changes)
    
    def simulate_green_wave(
        self,
        route: List[Dict],
        vehicle_speed: float,
        current_traffic: Dict
    ) -> Dict:
        """Simulate Green Wave effectiveness"""
        if not self.digital_twin:
            return {"error": "Digital twin not available"}
        
        return self.digital_twin.simulate_green_wave(route, vehicle_speed, current_traffic)
    
    # Green Wave Protocol
    def activate_green_wave(
        self,
        emergency_vehicle: Dict,
        route: List[Dict],
        traffic_lights: List[Dict]
    ) -> Dict:
        """Activate Green Wave for emergency vehicle"""
        if not self.green_wave:
            return {"error": "Green Wave controller not available"}
        
        return self.green_wave.calculate_green_wave(
            emergency_vehicle, route, traffic_lights
        )
    
    def update_green_wave(
        self,
        session_id: str,
        new_location: Dict,
        new_speed: float
    ) -> Dict:
        """Update active Green Wave"""
        if not self.green_wave:
            return {"error": "Green Wave controller not available"}
        
        return self.green_wave.update_green_wave(session_id, new_location, new_speed)
    
    def deactivate_green_wave(
        self,
        session_id: str,
        reason: str = "vehicle_passed"
    ) -> Dict:
        """Deactivate Green Wave"""
        if not self.green_wave:
            return {"error": "Green Wave controller not available"}
        
        return self.green_wave.deactivate_green_wave(session_id, reason)
    
    # Health Check
    def health_check(self) -> Dict:
        """Check status of all AI models"""
        return {
            "event_detector": self.event_detector is not None,
            "speed_optimizer": self.speed_optimizer is not None,
            "density_estimator": self.density_estimator is not None,
            "digital_twin": self.digital_twin is not None,
            "green_wave": self.green_wave is not None
        }


# Singleton instance
_manager_instance = None

def get_ai_manager(config: Optional[Dict] = None) -> AIModelManager:
    """Get or create AI Model Manager singleton"""
    global _manager_instance
    if _manager_instance is None:
        _manager_instance = AIModelManager(config)
    return _manager_instance
