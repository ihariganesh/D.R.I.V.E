"""
AI Model: Digital Twin Simulator
Simulates traffic flow to predict impact of manual overrides
"""
import numpy as np
from typing import Dict, List
from datetime import datetime, timedelta

class DigitalTwinSimulator:
    def __init__(self, simulation_duration: int = 5):
        """
        Initialize Digital Twin simulation engine
        
        Args:
            simulation_duration: Simulation time in seconds
        """
        self.duration = simulation_duration
        self.timestep = 0.1  # 100ms timesteps
        
    def simulate_override(
        self,
        current_state: Dict,
        proposed_changes: Dict
    ) -> Dict:
        """
        Simulate the impact of a manual override
        
        Args:
            current_state: Current traffic state (speeds, flows, events)
            proposed_changes: Proposed override changes
            
        Returns:
            Simulation results with predictions and warnings
        """
        # Extract current state
        current_speed_limit = current_state.get("speed_limit", 60)
        vehicle_count = current_state.get("vehicle_count", 30)
        avg_speed = current_state.get("avg_speed", 50)
        congestion_level = current_state.get("congestion_level", 0.3)
        
        # Extract proposed changes
        new_speed_limit = proposed_changes.get("speed_limit", current_speed_limit)
        
        # Run simulation
        steps = int(self.duration / self.timestep)
        results = {
            "timestamps": [],
            "congestion_levels": [],
            "avg_speeds": [],
            "queue_lengths": []
        }
        
        # Simulate each timestep
        sim_congestion = congestion_level
        sim_speed = avg_speed
        sim_queue = vehicle_count * congestion_level
        
        for step in range(steps):
            t = step * self.timestep
            
            # Model traffic dynamics
            speed_diff = new_speed_limit - current_speed_limit
            
            # Speed limit increase -> potential congestion reduction
            if speed_diff > 0:
                sim_congestion *= 0.98  # Gradual improvement
                sim_speed = min(new_speed_limit, sim_speed * 1.02)
                sim_queue *= 0.97
            # Speed limit decrease -> potential congestion increase
            elif speed_diff < 0:
                sim_congestion = min(1.0, sim_congestion * 1.03)
                sim_speed *= 0.98
                sim_queue *= 1.05
            
            results["timestamps"].append(t)
            results["congestion_levels"].append(sim_congestion)
            results["avg_speeds"].append(sim_speed)
            results["queue_lengths"].append(sim_queue)
        
        # Analyze results
        final_congestion = results["congestion_levels"][-1]
        final_speed = results["avg_speeds"][-1]
        final_queue = results["queue_lengths"][-1]
        
        # Generate predictions
        congestion_change = final_congestion - congestion_level
        speed_change = final_speed - avg_speed
        queue_change = final_queue - (vehicle_count * congestion_level)
        
        # Generate warnings
        warnings = []
        if congestion_change > 0.2:
            warnings.append({
                "severity": "high",
                "message": f"Congestion may increase by {congestion_change*100:.0f}%",
                "metric": "congestion"
            })
        if queue_change > 10:
            warnings.append({
                "severity": "medium",
                "message": f"Queue length may increase by {queue_change:.0f} vehicles",
                "metric": "queue_length"
            })
        if final_speed < 20:
            warnings.append({
                "severity": "high",
                "message": "Traffic may slow to critical levels",
                "metric": "speed"
            })
        
        # Generate recommendation
        if len(warnings) == 0:
            recommendation = "approve"
        elif any(w["severity"] == "high" for w in warnings):
            recommendation = "reject"
        else:
            recommendation = "caution"
        
        return {
            "simulation_duration": self.duration,
            "timesteps": steps,
            "results": results,
            "predicted_metrics": {
                "final_congestion_level": round(final_congestion, 3),
                "final_avg_speed": round(final_speed, 1),
                "final_queue_length": round(final_queue, 1),
                "congestion_change": round(congestion_change, 3),
                "speed_change": round(speed_change, 1),
                "queue_change": round(queue_change, 1)
            },
            "warnings": warnings,
            "recommendation": recommendation,
            "explanation": self._generate_explanation(
                current_speed_limit, new_speed_limit, 
                congestion_change, warnings
            )
        }
    
    def simulate_green_wave(
        self,
        route: List[Dict],
        vehicle_speed: float,
        current_traffic: Dict
    ) -> Dict:
        """
        Simulate Green Wave protocol for emergency vehicle
        
        Args:
            route: List of intersections with traffic lights
            vehicle_speed: Emergency vehicle speed (km/h)
            current_traffic: Current traffic state
            
        Returns:
            Simulation of green wave effectiveness
        """
        total_distance = sum(seg.get("distance", 0) for seg in route)
        travel_time_without = total_distance / (vehicle_speed / 3.6)  # Convert to m/s
        
        # Estimate delays at red lights
        red_light_delay = 0
        for intersection in route:
            if intersection.get("current_state") == "red":
                red_light_delay += intersection.get("red_duration", 30)
        
        # With green wave: minimal delays
        green_wave_delay = len(route) * 2  # 2 seconds per intersection
        
        travel_time_with = (total_distance / (vehicle_speed / 3.6)) + green_wave_delay
        time_saved = travel_time_without + red_light_delay - travel_time_with
        
        return {
            "total_distance": total_distance,
            "intersections": len(route),
            "travel_time_without_green_wave": round(travel_time_without + red_light_delay, 1),
            "travel_time_with_green_wave": round(travel_time_with, 1),
            "time_saved_seconds": round(time_saved, 1),
            "effectiveness": round(time_saved / (travel_time_without + red_light_delay), 2)
        }
    
    def _generate_explanation(
        self,
        current_limit: int,
        new_limit: int,
        congestion_change: float,
        warnings: List[Dict]
    ) -> str:
        """Generate human-readable explanation"""
        if new_limit > current_limit:
            action = f"Increasing speed limit from {current_limit} to {new_limit} km/h"
        elif new_limit < current_limit:
            action = f"Decreasing speed limit from {current_limit} to {new_limit} km/h"
        else:
            return "No speed limit change proposed"
        
        if congestion_change > 0.1:
            impact = f"may increase congestion by {congestion_change*100:.0f}%"
        elif congestion_change < -0.1:
            impact = f"may reduce congestion by {abs(congestion_change)*100:.0f}%"
        else:
            impact = "will have minimal impact on congestion"
        
        explanation = f"{action} {impact}."
        
        if warnings:
            explanation += f" {len(warnings)} warning(s) detected."
        
        return explanation
