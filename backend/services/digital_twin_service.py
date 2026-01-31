from typing import Dict
import time
import random
from datetime import datetime
from services.ai_service import get_ai_service

async def run_digital_twin_simulation(
    input_state: Dict,
    proposed_changes: Dict,
    duration: int,
    db
) -> Dict:
    """
    Run Digital Twin simulation to predict outcome of manual override
    
    This is Innovation #3: Digital Twin Replay
    - Simulates proposed changes for 5 seconds
    - Predicts traffic flow impact
    - Warns if override would cause congestion
    - "Predictive Human-in-the-Loop Control"
    
    Args:
        input_state: Current traffic state
        proposed_changes: Proposed manual override changes
        duration: Simulation duration in seconds
        db: Database session
    
    Returns:
        Dict with simulation results, predictions, and recommendations
    """
    start_time = time.time()
    
    # Extract current state
    current_traffic = input_state.get("traffic_metrics", {})
    current_lights = input_state.get("traffic_lights", {})
    current_speeds = input_state.get("speed_limits", {})
    
    # Extract proposed changes
    override_type = proposed_changes.get("override_type")
    entity_id = proposed_changes.get("entity_id")
    new_value = proposed_changes.get("new_value")
    
    # Initialize simulation results
    warnings = []
    predicted_metrics = {}
    recommendation = "approve"
    
    # Call real AI Simulator
    ai_service = get_ai_service()
    ai_results = ai_service.simulate_override(input_state, proposed_changes)
    
    # Use AI results if available
    if "error" not in ai_results:
        predicted_metrics = ai_results.get("predicted_metrics", {})
        warnings.extend(ai_results.get("warnings", []))
        if ai_results.get("recommendation"):
            recommendation = ai_results.get("recommendation")
    else:
        # Fallback to local heuristic simulation
        if override_type == "traffic_light":
            ...
    
    # Calculate execution time
    execution_time = int((time.time() - start_time) * 1000)
    
    # Build comprehensive results
    results = {
        "simulation_successful": True,
        "duration_simulated": duration,
        "timesteps": duration * 10,  # 0.1s timesteps
        "initial_state": input_state,
        "final_state": {
            "traffic_flow": predicted_metrics.get("traffic_flow", current_traffic.get("flow", 0)),
            "congestion_level": predicted_metrics.get("congestion_level", 0.5),
            "average_speed": predicted_metrics.get("average_speed", 45),
            "queue_lengths": predicted_metrics.get("queue_lengths", {})
        },
        "changes_applied": proposed_changes
    }
    
    return {
        "results": results,
        "predicted_metrics": predicted_metrics,
        "warnings": warnings,
        "recommendation": recommendation,
        "execution_time_ms": execution_time
    }

def simulate_traffic_light_override(
    current_traffic: Dict,
    current_lights: Dict,
    light_id: str,
    new_state: str
) -> Dict:
    """Simulate traffic light override impact"""
    base_flow = current_traffic.get("flow_rate", 400)
    base_congestion = current_traffic.get("congestion_level", 0.5)
    
    # Forcing red light increases congestion
    if new_state == "red":
        congestion_increase = 0.25 + random.uniform(0, 0.15)
        queue_length = int(base_flow * 0.15)  # Vehicles queuing
        flow_decrease = 0.3
    # Forcing green reduces congestion temporarily
    elif new_state == "green":
        congestion_increase = -0.1
        queue_length = max(0, int(base_flow * 0.05))
        flow_decrease = -0.1
    else:
        congestion_increase = 0.05
        queue_length = int(base_flow * 0.08)
        flow_decrease = 0.1
    
    return {
        "congestion_increase": congestion_increase,
        "new_congestion_level": min(1.0, base_congestion + congestion_increase),
        "queue_length": queue_length,
        "traffic_flow": base_flow * (1 - flow_decrease),
        "affected_roads": ["main_approach", "side_street_1", "side_street_2"]
    }

def simulate_speed_limit_override(
    current_traffic: Dict,
    current_speeds: Dict,
    road_id: str,
    new_speed: int
) -> Dict:
    """Simulate speed limit override impact"""
    current_avg_speed = current_traffic.get("average_speed", 55)
    current_flow = current_traffic.get("flow_rate", 400)
    
    speed_diff = abs(int(new_speed) - current_avg_speed)
    
    # Large speed changes increase risk
    accident_risk_increase = min(0.5, speed_diff / 100)
    
    # Lower speeds reduce flow but may improve safety
    if int(new_speed) < current_avg_speed:
        flow_impact = -0.15
        congestion_increase = 0.1
    else:
        flow_impact = 0.1
        congestion_increase = -0.05
    
    return {
        "accident_risk_increase": accident_risk_increase,
        "traffic_flow": current_flow * (1 + flow_impact),
        "average_speed": (current_avg_speed + int(new_speed)) / 2,
        "congestion_increase": congestion_increase,
        "speed_compliance_rate": max(0.6, 1 - (speed_diff / 100))
    }

def simulate_sign_board_override(
    current_traffic: Dict,
    sign_id: str,
    new_message: str
) -> Dict:
    """Simulate sign board message override impact"""
    return {
        "driver_awareness": 0.85,
        "expected_response_time": 3.5,  # seconds
        "impact_radius_meters": 500
    }
