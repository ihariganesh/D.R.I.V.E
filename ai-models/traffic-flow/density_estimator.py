"""
AI Model: Traffic Density Estimation
Uses YOLO v8 for vehicle detection and counting
"""
import torch
import cv2
import numpy as np
from ultralytics import YOLO
from typing import Dict, List, Tuple

class TrafficDensityEstimator:
    def __init__(self, model_path: str = "yolov8n.pt"):
        """Initialize YOLO model for vehicle detection"""
        self.model = YOLO(model_path)
        self.vehicle_classes = [2, 3, 5, 7]  # car, motorcycle, bus, truck
        
    def process_frame(self, frame: np.ndarray) -> Dict:
        """
        Process a single frame to detect vehicles
        
        Returns:
            Dict with vehicle count, density, and average speed estimate
        """
        results = self.model(frame, classes=self.vehicle_classes)
        
        vehicle_count = 0
        detections = []
        
        for result in results:
            boxes = result.boxes
            for box in boxes:
                x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                conf = box.conf[0].cpu().numpy()
                cls = int(box.cls[0].cpu().numpy())
                
                vehicle_count += 1
                detections.append({
                    "bbox": [float(x1), float(y1), float(x2), float(y2)],
                    "confidence": float(conf),
                    "class": cls
                })
        
        # Calculate density (vehicles per square meter of road)
        frame_area = frame.shape[0] * frame.shape[1] / 1000000  # Convert to square meters
        density = vehicle_count / frame_area if frame_area > 0 else 0
        
        # Estimate congestion level (0-1)
        congestion_level = min(1.0, vehicle_count / 50)  # Normalized to max 50 vehicles
        
        return {
            "vehicle_count": vehicle_count,
            "density": density,
            "congestion_level": congestion_level,
            "detections": detections
        }
    
    def estimate_speed(self, current_positions: List, previous_positions: List, 
                      fps: int = 30) -> float:
        """
        Estimate average vehicle speed using tracking
        """
        if not current_positions or not previous_positions:
            return 0.0
        
        # Calculate displacement between frames
        # This is a simplified version - production would use proper tracking
        total_speed = 0
        count = 0
        
        for curr_pos in current_positions:
            # Find closest previous position
            min_dist = float('inf')
            for prev_pos in previous_positions:
                dist = np.linalg.norm(np.array(curr_pos) - np.array(prev_pos))
                if dist < min_dist:
                    min_dist = dist
            
            # Convert pixel displacement to km/h (calibration needed)
            speed_kmh = min_dist * fps * 3.6 / 10  # Rough estimate
            total_speed += speed_kmh
            count += 1
        
        return total_speed / count if count > 0 else 0.0
