"""
AI Model: Green Wave Controller
Manages emergency vehicle routing and traffic light coordination
"""
import numpy as np
from typing import Dict, List, Tuple
from datetime import datetime, timedelta

class GreenWaveController:
    def __init__(self, advance_time: int = 45):
        """
        Initialize Green Wave controller
        
        Args:
            advance_time: Seconds ahead to clear path
        """
        self.advance_time = advance_time
        
    def calculate_green_wave(
        self,
        emergency_vehicle: Dict,
        route: List[Dict],
        traffic_lights: List[Dict]
    ) -> Dict:
        """
        Calculate Green Wave protocol for emergency vehicle
        
        Args:
            emergency_vehicle: Emergency vehicle data (location, speed, type)
            route: Predicted route with waypoints
            traffic_lights: Traffic lights along the route
            
        Returns:
            Green Wave activation plan with timing
        """
        vehicle_location = emergency_vehicle.get("current_location")
        vehicle_speed = emergency_vehicle.get("speed_kmh", 80)
        vehicle_type = emergency_vehicle.get("vehicle_type", "ambulance")
        
        # Calculate ETA to each traffic light
        light_schedule = []
        
        for light in traffic_lights:
            light_location = light.get("location")
            distance = self._calculate_distance(vehicle_location, light_location)
            
            # Calculate time to reach this light
            time_to_reach = (distance / 1000) / (vehicle_speed / 3600)  # Convert to seconds
            
            # When to turn light green (advance_time seconds before arrival)
            activation_time = datetime.now() + timedelta(seconds=max(0, time_to_reach - self.advance_time))
            
            # How long to keep it green
            green_duration = self.advance_time + 10  # Extra buffer
            
            light_schedule.append({
                "light_id": light.get("light_id"),
                "junction_id": light.get("junction_id"),
                "distance_meters": distance,
                "time_to_reach_seconds": round(time_to_reach, 1),
                "activation_time": activation_time.isoformat(),
                "green_duration_seconds": green_duration,
                "current_state": light.get("current_state"),
                "action": "turn_green" if light.get("current_state") != "green" else "maintain_green"
            })
        
        # Calculate cross-traffic speed reductions
        cross_traffic_zones = self._identify_cross_traffic(traffic_lights, route)
        
        return {
            "vehicle_id": emergency_vehicle.get("vehicle_id"),
            "vehicle_type": vehicle_type,
            "route_length_meters": sum(seg.get("distance", 0) for seg in route),
            "affected_lights": len(light_schedule),
            "light_schedule": light_schedule,
            "cross_traffic_zones": cross_traffic_zones,
            "total_eta_seconds": light_schedule[-1]["time_to_reach_seconds"] if light_schedule else 0,
            "advance_time_seconds": self.advance_time,
            "activated_at": datetime.now().isoformat()
        }
    
    def update_green_wave(
        self,
        session_id: str,
        new_location: Dict,
        new_speed: float
    ) -> Dict:
        """
        Update Green Wave based on vehicle's new position
        
        Args:
            session_id: Active Green Wave session ID
            new_location: Updated vehicle location
            new_speed: Updated vehicle speed
            
        Returns:
            Updated Green Wave schedule
        """
        # In production, this would fetch the active session and recalculate
        return {
            "session_id": session_id,
            "status": "updated",
            "message": "Green Wave schedule updated based on new vehicle position"
        }
    
    def deactivate_green_wave(
        self,
        session_id: str,
        reason: str = "vehicle_passed"
    ) -> Dict:
        """
        Deactivate Green Wave and restore normal traffic control
        
        Args:
            session_id: Active Green Wave session ID
            reason: Reason for deactivation
            
        Returns:
            Deactivation confirmation
        """
        return {
            "session_id": session_id,
            "status": "deactivated",
            "reason": reason,
            "deactivated_at": datetime.now().isoformat(),
            "message": "Traffic lights restored to normal operation"
        }
    
    def _calculate_distance(self, loc1: Dict, loc2: Dict) -> float:
        """
        Calculate distance between two geographic points (Haversine formula)
        
        Returns:
            Distance in meters
        """
        # Simplified - in production use proper geographic calculation
        lat1, lon1 = loc1.get("lat", 0), loc1.get("lon", 0)
        lat2, lon2 = loc2.get("lat", 0), loc2.get("lon", 0)
        
        # Haversine formula
        R = 6371000  # Earth radius in meters
        phi1 = np.radians(lat1)
        phi2 = np.radians(lat2)
        delta_phi = np.radians(lat2 - lat1)
        delta_lambda = np.radians(lon2 - lon1)
        
        a = np.sin(delta_phi/2)**2 + np.cos(phi1) * np.cos(phi2) * np.sin(delta_lambda/2)**2
        c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1-a))
        
        return R * c
    
    def _identify_cross_traffic(
        self,
        traffic_lights: List[Dict],
        route: List[Dict]
    ) -> List[Dict]:
        """
        Identify cross-traffic zones that need speed reduction
        
        Returns:
            List of zones with recommended speed reductions
        """
        zones = []
        
        for light in traffic_lights:
            junction_id = light.get("junction_id")
            
            # Identify perpendicular roads
            zones.append({
                "junction_id": junction_id,
                "location": light.get("location"),
                "recommended_speed_reduction": 20,  # km/h
                "duration_seconds": self.advance_time + 15,
                "reason": "Emergency vehicle approaching"
            })
        
        return zones
