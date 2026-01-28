"""
Camera Service - Processes video feeds from traffic cameras
Detects vehicles, events, and sends data to backend
"""
import cv2
import requests
import os
import time
from dotenv import load_dotenv

load_dotenv()

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

class CameraProcessor:
    def __init__(self, camera_id: str, video_source: str):
        self.camera_id = camera_id
        self.video_source = video_source
        self.cap = None
        
    def start(self):
        """Start processing camera feed"""
        print(f"Starting camera processor for {self.camera_id}")
        self.cap = cv2.VideoCapture(self.video_source)
        
        while True:
            ret, frame = self.cap.read()
            if not ret:
                print(f"Failed to read frame from {self.camera_id}")
                break
            
            # Process frame (placeholder)
            self.process_frame(frame)
            
            # Send to backend every 5 seconds
            time.sleep(5)
    
    def process_frame(self, frame):
        """Process a single frame"""
        # In production: run AI models here
        # - Vehicle detection
        # - Event detection
        # - Speed estimation
        pass
    
    def stop(self):
        """Stop camera processor"""
        if self.cap:
            self.cap.release()

if __name__ == "__main__":
    # Example usage
    processor = CameraProcessor("CAM001", 0)  # 0 for webcam
    processor.start()
