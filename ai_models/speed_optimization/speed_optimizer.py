"""
AI Model: Speed Limit Optimization
Calculates optimal speed limits based on traffic conditions and events
"""
import numpy as np
from typing import Dict, List
import os

class SpeedOptimizer:
    def __init__(self):
        """Initialize speed optimization model"""
        self.min_speed = int(os.getenv("MIN_SPEED_LIMIT", 20))
        self.max_speed = int(os.getenv("MAX_SPEED_LIMIT", 120))
        self.default_speed = int(os.getenv("DEFAULT_SPEED_LIMIT", 60))
        
    def calculate_optimal_speed(
        self,
        current_speed: int,
        vehicle_count: int,
        avg_speed: float,
        congestion_level: float,
        events: List[Dict],
        weather_condition: str = "clear"
    ) -> Dict:
        """
        Calculate optimal speed limit with XAI explanation
        
        Returns:
            Dict with new speed, explanation, and reasoning
        """
        # Start with current speed
        optimal_speed = current_speed
        factors = []
        adjustments = []
        
        # Factor 1: Traffic Density
        if vehicle_count > 50:
            adjustment = -20
            optimal_speed += adjustment
            factors.append("high_traffic_density")
            adjustments.append({
                "factor": "High traffic density",
                "adjustment": adjustment,
                "reason": f"{vehicle_count} vehicles detected"
            })
        elif vehicle_count < 10:
            adjustment = 10
            optimal_speed += adjustment
            factors.append("low_traffic_density")
            adjustments.append({
                "factor": "Low traffic density",
                "adjustment": adjustment,
                "reason": f"Only {vehicle_count} vehicles, safe to increase"
            })
        
        # Factor 2: Average Speed
        if avg_speed < 30 and current_speed > 40:
            adjustment = -15
            optimal_speed += adjustment
            factors.append("slow_moving_traffic")
            adjustments.append({
                "factor": "Slow-moving traffic",
                "adjustment": adjustment,
                "reason": f"Vehicles moving at {avg_speed:.1f} km/h"
            })
        
        # Factor 3: Congestion Level
        if congestion_level > 0.7:
            adjustment = -15
            optimal_speed += adjustment
            factors.append("high_congestion")
            adjustments.append({
                "factor": "High congestion level",
                "adjustment": adjustment,
                "reason": f"Congestion at {congestion_level*100:.0f}%"
            })
        
        # Factor 4: Events (accidents, debris, etc.)
        for event in events:
            if event.get("severity") == "high":
                adjustment = -25
                optimal_speed += adjustment
                factors.append(f"event_{event.get('event_type')}")
                adjustments.append({
                    "factor": f"{event.get('event_type')} detected",
                    "adjustment": adjustment,
                    "reason": f"Severity: {event.get('severity')}, Distance: {event.get('distance', 'N/A')}m"
                })
            elif event.get("severity") == "medium":
                adjustment = -15
                optimal_speed += adjustment
                factors.append(f"event_{event.get('event_type')}")
                adjustments.append({
                    "factor": f"{event.get('event_type')} detected",
                    "adjustment": adjustment,
                    "reason": f"Moderate severity event nearby"
                })
        
        # Factor 5: Weather Conditions
        weather_adjustments = {
            "rain": -15,
            "heavy_rain": -25,
            "fog": -20,
            "snow": -30,
            "ice": -40
        }
        if weather_condition in weather_adjustments:
            adjustment = weather_adjustments[weather_condition]
            optimal_speed += adjustment
            factors.append(f"weather_{weather_condition}")
            adjustments.append({
                "factor": f"Weather: {weather_condition}",
                "adjustment": adjustment,
                "reason": "Reduced visibility/traction"
            })
        
        # Clamp to limits
        optimal_speed = max(self.min_speed, min(self.max_speed, optimal_speed))
        
        # Round to nearest 5
        optimal_speed = round(optimal_speed / 5) * 5
        
        # Generate explanation (XAI)
        explanation = self._generate_explanation(
            current_speed, optimal_speed, adjustments
        )
        
        # Calculate confidence
        confidence = self._calculate_confidence(factors, adjustments)
        
        return {
            "current_speed": current_speed,
            "optimal_speed": optimal_speed,
            "speed_change": optimal_speed - current_speed,
            "explanation": explanation,
            "factors": factors,
            "adjustments": adjustments,
            "confidence": confidence,
            "reasoning": {
                "vehicle_count": vehicle_count,
                "avg_speed": avg_speed,
                "congestion_level": congestion_level,
                "events_detected": len(events),
                "weather": weather_condition
            }
        }
    
    def _generate_explanation(
        self, 
        current: int, 
        optimal: int, 
        adjustments: List[Dict]
    ) -> str:
        """Generate human-readable explanation (XAI)"""
        if optimal == current:
            return f"Speed limit maintained at {current} km/h - conditions are stable."
        
        change = optimal - current
        direction = "reduced" if change < 0 else "increased"
        
        main_factors = [adj["factor"] for adj in adjustments[:2]]  # Top 2 factors
        
        explanation = f"Speed limit {direction} to {optimal} km/h due to: "
        explanation += ", ".join(main_factors)
        
        if len(adjustments) > 2:
            explanation += f" and {len(adjustments) - 2} other factors"
        
        return explanation
    
    def _calculate_confidence(self, factors: List[str], adjustments: List[Dict]) -> float:
        """Calculate confidence score for the decision"""
        # Base confidence
        confidence = 0.7
        
        # More factors = higher confidence
        confidence += min(0.2, len(factors) * 0.04)
        
        # Large adjustments = slightly lower confidence
        total_adjustment = sum(abs(adj["adjustment"]) for adj in adjustments)
        if total_adjustment > 40:
            confidence -= 0.1
        
        return round(confidence, 2)
