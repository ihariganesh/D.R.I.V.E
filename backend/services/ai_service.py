import sys
from pathlib import Path
import os

# Add root project directory to sys.path to find ai-models
ROOT_DIR = Path(__file__).parent.parent.parent
sys.path.append(str(ROOT_DIR))

from ai_models.model_manager import get_ai_manager

class AIService:
    """
    Bridge service between FastAPI and AI models
    """
    def __init__(self):
        # Configuration for AI models
        config = {
            "yolo_model_path": os.getenv("YOLO_MODEL_PATH", "yolov8n.pt"),
            "simulation_duration": 5,
            "green_wave_advance_time": 45
        }
        self.manager = get_ai_manager(config)
        
    def get_status(self):
        return self.manager.health_check()
        
    def optimize_speed(self, current_state: dict):
        """
        Calls the AISpeedOptimizer
        """
        return self.manager.optimize_speed(
            current_speed=current_state.get("current_speed", 60),
            vehicle_count=current_state.get("vehicle_count", 0),
            avg_speed=current_state.get("avg_speed", 55),
            congestion_level=current_state.get("congestion_level", 0.1),
            events=current_state.get("events", []),
            weather=current_state.get("weather", "clear")
        )
        
    def simulate_override(self, current_state: dict, proposed_changes: dict):
        """
        Calls the Digital Twin Simulator
        """
        return self.manager.simulate_override(current_state, proposed_changes)

# Singleton
_ai_service = AIService()

def get_ai_service() -> AIService:
    return _ai_service
