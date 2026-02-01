"""
Camera Client - Surveillance Network Core B
Runs on individual laptops/cameras to detect and stream events

Features:
- Captures webcam/camera feed
- Runs YOLOv8 for object detection
- Detects events (people, vehicles, fire, running persons)
- Sends event alerts to central server via HTTP
"""

import cv2
import json
import time
import argparse
import logging
import requests
import threading
import numpy as np
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from collections import deque
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class DetectedEvent:
    """Represents a detected event"""
    event_type: str
    confidence: float
    timestamp: str
    camera_id: str
    location: Optional[str] = None
    bounding_box: Optional[List[int]] = None
    description: Optional[str] = None
    frame_number: int = 0
    severity: str = "low"


class YOLODetector:
    """YOLOv8 wrapper for object detection"""
    
    # Class labels for detection
    COCO_CLASSES = {
        0: 'person', 1: 'bicycle', 2: 'car', 3: 'motorcycle', 
        4: 'airplane', 5: 'bus', 6: 'train', 7: 'truck',
        8: 'boat', 9: 'traffic light', 10: 'fire hydrant',
        11: 'stop sign', 12: 'parking meter', 13: 'bench',
        14: 'bird', 15: 'cat', 16: 'dog', 17: 'horse',
        18: 'sheep', 19: 'cow', 20: 'elephant', 21: 'bear',
        22: 'zebra', 23: 'giraffe', 24: 'backpack', 25: 'umbrella',
        26: 'handbag', 27: 'tie', 28: 'suitcase', 29: 'frisbee',
        30: 'skis', 31: 'snowboard', 32: 'sports ball', 33: 'kite',
        34: 'baseball bat', 35: 'baseball glove', 36: 'skateboard',
        37: 'surfboard', 38: 'tennis racket', 39: 'bottle',
        40: 'wine glass', 41: 'cup', 42: 'fork', 43: 'knife',
        44: 'spoon', 45: 'bowl', 46: 'banana', 47: 'apple',
        48: 'sandwich', 49: 'orange', 50: 'broccoli', 51: 'carrot',
        52: 'hot dog', 53: 'pizza', 54: 'donut', 55: 'cake',
        56: 'chair', 57: 'couch', 58: 'potted plant', 59: 'bed',
        60: 'dining table', 61: 'toilet', 62: 'tv', 63: 'laptop',
        64: 'mouse', 65: 'remote', 66: 'keyboard', 67: 'cell phone',
        68: 'microwave', 69: 'oven', 70: 'toaster', 71: 'sink',
        72: 'refrigerator', 73: 'book', 74: 'clock', 75: 'vase',
        76: 'scissors', 77: 'teddy bear', 78: 'hair drier', 79: 'toothbrush'
    }
    
    # Event-triggering classes
    ALERT_CLASSES = ['person', 'car', 'truck', 'bus', 'motorcycle', 'bicycle']
    
    def __init__(self, model_path: str = "yolov8n.pt", confidence_threshold: float = 0.5):
        """
        Initialize YOLO detector
        
        Args:
            model_path: Path to YOLOv8 weights
            confidence_threshold: Minimum confidence for detections
        """
        self.model_path = model_path
        self.confidence_threshold = confidence_threshold
        self.model = None
        self._load_model()
    
    def _load_model(self):
        """Load YOLOv8 model"""
        try:
            from ultralytics import YOLO
            
            # Check if model exists
            if not os.path.exists(self.model_path):
                logger.info(f"Downloading YOLOv8 model...")
                self.model = YOLO('yolov8n.pt')  # Will download automatically
            else:
                self.model = YOLO(self.model_path)
            
            logger.info(f"YOLOv8 model loaded from {self.model_path}")
        except ImportError:
            logger.warning("ultralytics not installed. Using fallback detection.")
            self.model = None
        except Exception as e:
            logger.error(f"Error loading model: {e}")
            self.model = None
    
    def detect(self, frame: np.ndarray) -> List[Dict]:
        """
        Run detection on a frame
        
        Args:
            frame: BGR frame from OpenCV
            
        Returns:
            List of detections with class, confidence, and bounding box
        """
        if self.model is None:
            return self._fallback_detection(frame)
        
        try:
            # Run inference
            results = self.model(frame, verbose=False)[0]
            
            detections = []
            for box in results.boxes:
                class_id = int(box.cls[0])
                confidence = float(box.conf[0])
                
                if confidence < self.confidence_threshold:
                    continue
                
                class_name = self.COCO_CLASSES.get(class_id, f"class_{class_id}")
                bbox = box.xyxy[0].tolist()  # [x1, y1, x2, y2]
                
                detections.append({
                    'class': class_name,
                    'class_id': class_id,
                    'confidence': confidence,
                    'bbox': [int(x) for x in bbox]
                })
            
            return detections
            
        except Exception as e:
            logger.error(f"Detection error: {e}")
            return []
    
    def _fallback_detection(self, frame: np.ndarray) -> List[Dict]:
        """
        Fallback detection using basic CV techniques when YOLO unavailable
        Uses motion detection and color analysis
        """
        detections = []
        
        # Simple color-based fire detection (orange/red regions)
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        
        # Fire detection (orange-red colors)
        lower_fire = np.array([0, 100, 100])
        upper_fire = np.array([25, 255, 255])
        fire_mask = cv2.inRange(hsv, lower_fire, upper_fire)
        
        fire_contours, _ = cv2.findContours(fire_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        for contour in fire_contours:
            area = cv2.contourArea(contour)
            if area > 500:  # Minimum area threshold
                x, y, w, h = cv2.boundingRect(contour)
                detections.append({
                    'class': 'fire',
                    'class_id': 100,
                    'confidence': min(0.9, area / 5000),
                    'bbox': [x, y, x + w, y + h]
                })
        
        return detections


class MotionAnalyzer:
    """Analyzes motion to detect running, accidents, etc."""
    
    def __init__(self, history_size: int = 30):
        """
        Initialize motion analyzer
        
        Args:
            history_size: Number of frames to keep for motion analysis
        """
        self.history_size = history_size
        self.position_history: Dict[str, deque] = {}  # object_id -> positions
        self.bg_subtractor = cv2.createBackgroundSubtractorMOG2(
            history=500, varThreshold=16, detectShadows=True
        )
    
    def update(self, detections: List[Dict], frame_number: int) -> List[Dict]:
        """
        Update motion tracking and detect motion-based events
        
        Args:
            detections: List of YOLO detections
            frame_number: Current frame number
            
        Returns:
            List of motion-based events
        """
        events = []
        
        for det in detections:
            if det['class'] == 'person':
                bbox = det['bbox']
                center_x = (bbox[0] + bbox[2]) // 2
                center_y = (bbox[1] + bbox[3]) // 2
                
                # Create simple object ID based on position
                obj_id = f"person_{center_x // 50}_{center_y // 50}"
                
                if obj_id not in self.position_history:
                    self.position_history[obj_id] = deque(maxlen=self.history_size)
                
                self.position_history[obj_id].append({
                    'x': center_x,
                    'y': center_y,
                    'frame': frame_number
                })
                
                # Check for running (high velocity)
                if len(self.position_history[obj_id]) >= 5:
                    velocity = self._calculate_velocity(self.position_history[obj_id])
                    
                    if velocity > 50:  # Pixels per frame threshold for running
                        events.append({
                            'type': 'person_running',
                            'confidence': min(0.95, velocity / 100),
                            'bbox': bbox,
                            'velocity': velocity
                        })
        
        return events
    
    def _calculate_velocity(self, positions: deque) -> float:
        """Calculate average velocity from position history"""
        if len(positions) < 2:
            return 0
        
        velocities = []
        positions_list = list(positions)
        
        for i in range(1, len(positions_list)):
            prev = positions_list[i - 1]
            curr = positions_list[i]
            
            dx = curr['x'] - prev['x']
            dy = curr['y'] - prev['y']
            df = curr['frame'] - prev['frame']
            
            if df > 0:
                velocity = np.sqrt(dx**2 + dy**2) / df
                velocities.append(velocity)
        
        return np.mean(velocities) if velocities else 0


class CameraClient:
    """
    Camera client for surveillance network
    Captures video, detects events, and sends to server
    """
    
    def __init__(
        self,
        camera_id: str,
        server_url: str,
        video_source: int = 0,
        model_path: str = "yolov8n.pt",
        detection_interval: float = 0.5,  # Seconds between detections
        location: str = "Unknown"
    ):
        """
        Initialize camera client
        
        Args:
            camera_id: Unique camera identifier
            server_url: URL of the aggregator server
            video_source: Camera index (0 for webcam) or video file path
            model_path: Path to YOLOv8 model weights
            detection_interval: Time between detection runs
            location: Physical location description
        """
        self.camera_id = camera_id
        self.server_url = server_url.rstrip('/')
        self.video_source = video_source
        self.detection_interval = detection_interval
        self.location = location
        
        # Initialize components
        self.detector = YOLODetector(model_path)
        self.motion_analyzer = MotionAnalyzer()
        
        # State
        self.cap = None
        self.running = False
        self.frame_number = 0
        self.last_detection_time = 0
        self.events_sent = 0
        self.connection_failures = 0
        
        # Event throttling to prevent spam
        self.recent_events: Dict[str, float] = {}
        self.event_cooldown = 5.0  # Seconds between same event type
    
    def start(self):
        """Start camera capture and processing"""
        logger.info(f"Starting camera client {self.camera_id}")
        
        # Open video source
        self.cap = cv2.VideoCapture(self.video_source)
        
        if not self.cap.isOpened():
            logger.error(f"Failed to open video source: {self.video_source}")
            return False
        
        # Get camera properties
        width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = int(self.cap.get(cv2.CAP_PROP_FPS))
        
        logger.info(f"Camera opened: {width}x{height} @ {fps}fps")
        
        # Register with server
        self._register_with_server()
        
        self.running = True
        return True
    
    def stop(self):
        """Stop camera capture"""
        logger.info(f"Stopping camera client {self.camera_id}")
        self.running = False
        
        if self.cap:
            self.cap.release()
        
        # Notify server
        self._deregister_from_server()
    
    def run(self, show_preview: bool = True):
        """
        Main processing loop
        
        Args:
            show_preview: Whether to show live preview window
        """
        if not self.start():
            return
        
        try:
            while self.running:
                ret, frame = self.cap.read()
                
                if not ret:
                    logger.warning("Failed to read frame")
                    time.sleep(0.1)
                    continue
                
                self.frame_number += 1
                current_time = time.time()
                
                # Run detection at specified interval
                if current_time - self.last_detection_time >= self.detection_interval:
                    self._process_frame(frame)
                    self.last_detection_time = current_time
                
                # Show preview if enabled
                if show_preview:
                    cv2.imshow(f"Camera: {self.camera_id}", frame)
                    
                    # Check for quit
                    if cv2.waitKey(1) & 0xFF == ord('q'):
                        logger.info("Quit signal received")
                        break
                
        except KeyboardInterrupt:
            logger.info("Interrupted by user")
        except Exception as e:
            logger.error(f"Error in processing loop: {e}")
        finally:
            self.stop()
            cv2.destroyAllWindows()
    
    def _process_frame(self, frame: np.ndarray):
        """Process a single frame for events"""
        # Run YOLO detection
        detections = self.detector.detect(frame)
        
        # Run motion analysis
        motion_events = self.motion_analyzer.update(detections, self.frame_number)
        
        # Generate events from detections
        events = []
        
        # Object detections
        for det in detections:
            if det['class'] in YOLODetector.ALERT_CLASSES:
                event = DetectedEvent(
                    event_type=det['class'],
                    confidence=det['confidence'],
                    timestamp=datetime.now().isoformat(),
                    camera_id=self.camera_id,
                    location=self.location,
                    bounding_box=det['bbox'],
                    description=f"{det['class']} detected with {det['confidence']:.2%} confidence",
                    frame_number=self.frame_number,
                    severity=self._get_severity(det['class'])
                )
                events.append(event)
        
        # Fire detection (from fallback or YOLO)
        for det in detections:
            if det['class'] == 'fire':
                event = DetectedEvent(
                    event_type='fire',
                    confidence=det['confidence'],
                    timestamp=datetime.now().isoformat(),
                    camera_id=self.camera_id,
                    location=self.location,
                    bounding_box=det['bbox'],
                    description="Fire or flames detected!",
                    frame_number=self.frame_number,
                    severity='critical'
                )
                events.append(event)
        
        # Motion-based events
        for motion_event in motion_events:
            event = DetectedEvent(
                event_type=motion_event['type'],
                confidence=motion_event['confidence'],
                timestamp=datetime.now().isoformat(),
                camera_id=self.camera_id,
                location=self.location,
                bounding_box=motion_event.get('bbox'),
                description=f"Person running detected (velocity: {motion_event.get('velocity', 0):.1f})",
                frame_number=self.frame_number,
                severity='medium'
            )
            events.append(event)
        
        # Send events to server (with throttling)
        for event in events:
            self._send_event(event)
    
    def _get_severity(self, class_name: str) -> str:
        """Get severity level for a detection class"""
        severity_map = {
            'person': 'low',
            'car': 'low',
            'truck': 'low',
            'motorcycle': 'low',
            'bicycle': 'low',
            'fire': 'critical',
            'person_running': 'medium'
        }
        return severity_map.get(class_name, 'low')
    
    def _send_event(self, event: DetectedEvent):
        """
        Send event to server with throttling
        
        Args:
            event: Event to send
        """
        # Check cooldown
        event_key = f"{event.event_type}_{event.camera_id}"
        current_time = time.time()
        
        if event_key in self.recent_events:
            if current_time - self.recent_events[event_key] < self.event_cooldown:
                return  # Skip, event sent too recently
        
        # Update recent events
        self.recent_events[event_key] = current_time
        
        # Send to server
        try:
            response = requests.post(
                f"{self.server_url}/api/events",
                json=asdict(event),
                timeout=5
            )
            
            if response.status_code == 200:
                self.events_sent += 1
                logger.info(f"Event sent: {event.event_type} ({self.events_sent} total)")
                self.connection_failures = 0
            else:
                logger.warning(f"Server returned status {response.status_code}")
                
        except requests.exceptions.RequestException as e:
            self.connection_failures += 1
            if self.connection_failures % 10 == 1:
                logger.warning(f"Failed to send event: {e}")
    
    def _register_with_server(self):
        """Register this camera with the server"""
        try:
            response = requests.post(
                f"{self.server_url}/api/cameras/register",
                json={
                    'camera_id': self.camera_id,
                    'location': self.location,
                    'status': 'online',
                    'capabilities': ['object_detection', 'motion_analysis'],
                    'registered_at': datetime.now().isoformat()
                },
                timeout=5
            )
            
            if response.status_code == 200:
                logger.info(f"Registered with server: {self.camera_id}")
            else:
                logger.warning(f"Registration failed: {response.status_code}")
                
        except requests.exceptions.RequestException as e:
            logger.warning(f"Could not register with server: {e}")
    
    def _deregister_from_server(self):
        """Deregister this camera from the server"""
        try:
            response = requests.post(
                f"{self.server_url}/api/cameras/deregister",
                json={
                    'camera_id': self.camera_id,
                    'deregistered_at': datetime.now().isoformat()
                },
                timeout=5
            )
            
            if response.status_code == 200:
                logger.info(f"Deregistered from server: {self.camera_id}")
                
        except requests.exceptions.RequestException as e:
            logger.debug(f"Could not deregister from server: {e}")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='Surveillance Camera Client')
    parser.add_argument(
        '--camera-id',
        default='CAM001',
        help='Unique camera identifier'
    )
    parser.add_argument(
        '--server',
        default='http://localhost:5001',
        help='Server URL'
    )
    parser.add_argument(
        '--source',
        default=0,
        help='Video source (camera index or file path)'
    )
    parser.add_argument(
        '--model',
        default='yolov8n.pt',
        help='Path to YOLOv8 model'
    )
    parser.add_argument(
        '--interval',
        type=float,
        default=0.5,
        help='Detection interval in seconds'
    )
    parser.add_argument(
        '--location',
        default='Unknown Location',
        help='Physical location description'
    )
    parser.add_argument(
        '--no-preview',
        action='store_true',
        help='Disable preview window'
    )
    
    args = parser.parse_args()
    
    # Parse video source
    try:
        video_source = int(args.source)
    except ValueError:
        video_source = args.source  # File path
    
    # Create and run client
    client = CameraClient(
        camera_id=args.camera_id,
        server_url=args.server,
        video_source=video_source,
        model_path=args.model,
        detection_interval=args.interval,
        location=args.location
    )
    
    client.run(show_preview=not args.no_preview)


if __name__ == "__main__":
    main()
