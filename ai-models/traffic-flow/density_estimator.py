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
        """Initialize YOLO model for detection"""
        self.model = YOLO(model_path)
        self.vehicle_classes = [2, 3, 5, 7]  # car, motorcycle, bus, truck
        self.pedestrian_classes = [0]       # person
        
    def process_frame(self, frame: np.ndarray) -> Dict:
        """
        Process a single frame to detect vehicles and pedestrians
        """
        # Detect vehicles
        vehicle_results = self.model(frame, classes=self.vehicle_classes, verbose=False)
        # Detect pedestrians
        pedestrian_results = self.model(frame, classes=self.pedestrian_classes, verbose=False)
        
        vehicle_count = 0
        pedestrian_count = 0
        detections = []
        
        for result in vehicle_results:
            boxes = result.boxes
            for box in boxes:
                x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                conf = box.conf[0].cpu().numpy()
                cls = int(box.cls[0].cpu().numpy())
                vehicle_count += 1
                detections.append({
                    "type": "vehicle",
                    "bbox": [float(x1), float(y1), float(x2), float(y2)],
                    "confidence": float(conf),
                    "class": cls
                })
        
        for result in pedestrian_results:
            boxes = result.boxes
            for box in boxes:
                x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                conf = box.conf[0].cpu().numpy()
                cls = int(box.cls[0].cpu().numpy())
                pedestrian_count += 1
                detections.append({
                    "type": "pedestrian",
                    "bbox": [float(x1), float(y1), float(x2), float(y2)],
                    "confidence": float(conf),
                    "class": cls
                })

        # Calculate density
        frame_area = frame.shape[0] * frame.shape[1] / 1000000 
        vehicle_density = vehicle_count / frame_area if frame_area > 0 else 0
        pedestrian_density = pedestrian_count / (frame_area / 4) if frame_area > 0 else 0 # Normalized to typical sidewalk area
        
        congestion_level = min(1.0, vehicle_count / 50)
        pedestrian_risk = min(1.0, pedestrian_count / 20) # Risk increases with crowd
        
        return {
            "vehicle_count": vehicle_count,
            "pedestrian_count": pedestrian_count,
            "vehicle_density": vehicle_density,
            "pedestrian_density": pedestrian_density,
            "congestion_level": congestion_level,
            "pedestrian_risk_level": pedestrian_risk,
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
