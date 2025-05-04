"""
Vision Processor - Core component for computer vision tasks
"""
import cv2
import numpy as np
import logging
import threading
import time
from collections import deque

from models.object_detector import ObjectDetector
from models.scene_analyzer import SceneAnalyzer

# Set up logging
logger = logging.getLogger(__name__)

class VisionProcessor:
    """Main class for processing camera frames and providing visual understanding."""
    
    def __init__(self, settings):
        """Initialize the vision processor.
        
        Args:
            settings (Settings): Application settings object
        """
        self.settings = settings
        self.camera = None
        self.camera_lock = threading.Lock()
        self.frame_width = 640
        self.frame_height = 480
        
        # Initialize models
        self.object_detector = ObjectDetector(
            model_path=settings.get('models', 'object_detection_model'),
            confidence_threshold=settings.get('vision', 'object_confidence_threshold', 0.5)
        )
        
        self.scene_analyzer = SceneAnalyzer(
            model_path=settings.get('models', 'scene_analysis_model')
        )
        
        # Frame buffer to store recent frames
        self.frame_buffer = deque(maxlen=10)
        
        # Processing results
        self.detected_objects = []
        self.scene_description = ""
        self.obstacles = []
        self.current_text = ""
        self.emergency_data = None
        
        # Thread for continuous frame capture
        self.capture_thread = None
        self.stop_capture = False
        
        logger.info("Vision processor initialized")
    
    def connect_camera(self, camera_id=0):
        """Connect to the camera device.
        
        Args:
            camera_id (int): Camera device ID
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            with self.camera_lock:
                self.camera = cv2.VideoCapture(camera_id)
                self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, self.frame_width)
                self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, self.frame_height)
                
                if not self.camera.isOpened():
                    logger.error(f"Failed to open camera with ID {camera_id}")
                    return False
                
                # Start capture thread
                self.stop_capture = False
                self.capture_thread = threading.Thread(target=self._capture_frames)
                self.capture_thread.daemon = True
                self.capture_thread.start()
                
                logger.info(f"Successfully connected to camera {camera_id}")
                return True
                
        except Exception as e:
            logger.error(f"Error connecting to camera: {str(e)}")
            return False
    
    def _capture_frames(self):
        """Continuously capture frames from the camera in a background thread."""
        while not self.stop_capture and self.camera is not None:
            try:
                with self.camera_lock:
                    if not self.camera.isOpened():
                        logger.error("Camera disconnected")
                        break
                    
                    ret, frame = self.camera.read()
                
                if ret:
                    # Add frame to buffer
                    self.frame_buffer.append(frame.copy())
                else:
                    logger.warning("Failed to capture frame")
                    time.sleep(0.1)
            
            except Exception as e:
                logger.error(f"Error capturing frame: {str(e)}")
                time.sleep(0.1)
    
    def get_frame(self):
        """Get the most recent frame from the buffer.
        
        Returns:
            numpy.ndarray: The most recent frame, or None if buffer is empty
        """
        if not self.frame_buffer:
            return None
        return self.frame_buffer[-1].copy()
    
    def process_frame(self, frame):
        """Process a single frame with all vision models.
        
        Args:
            frame (numpy.ndarray): Camera frame to process
        """
        if frame is None:
            return
        
        try:
            # Run object detection
            self.detected_objects = self.object_detector.detect_objects(frame)
            
            # Identify potential obstacles
            self.obstacles = self.object_detector.classify_obstacles(self.detected_objects)
            
            # Analyze scene
            self.scene_description = self.scene_analyzer.describe_scene(frame)
            
            # Perform OCR if enabled
            if self.settings.get('vision', 'enable_ocr', True):
                self.current_text = self.read_text(frame)
                
            # Check for emergency situations
            self._analyze_emergency_situations(frame)
            
        except Exception as e:
            logger.error(f"Error processing frame: {str(e)}")
    
    def detect_obstacles(self):
        """Get list of detected obstacles from the current frame.
        
        Returns:
            list: List of obstacle objects with position and type information
        """
        return self.obstacles
    
    def analyze_environment(self):
        """Analyze the current environment.
        
        Returns:
            dict: Dictionary containing environment data
        """
        env_data = {
            'scene_type': self.scene_analyzer.identify_environment_type(),
            'objects': self.detected_objects,
            'description': self.scene_description,
            'obstacles': self.obstacles
        }
        return env_data
    
    def read_text(self, frame):
        """Perform OCR to read text in the environment.
        
        Args:
            frame (numpy.ndarray): Camera frame to process
            
        Returns:
            str: Extracted text from the frame
        """
        try:
            # Use scene analyzer's OCR functionality
            text = self.scene_analyzer.extract_text(frame)
            return text
        except Exception as e:
            logger.error(f"Error reading text: {str(e)}")
            return ""
    
    def get_environment_data(self):
        """Get current environment data for navigation.
        
        Returns:
            dict: Dictionary with environment data
        """
        return {
            'objects': self.detected_objects,
            'obstacles': self.obstacles,
            'scene_type': self.scene_analyzer.get_scene_type(),
            'landmarks': self.scene_analyzer.get_landmarks()
        }
    
    def _analyze_emergency_situations(self, frame):
        """Analyze the frame for potential emergency situations.
        
        Args:
            frame (numpy.ndarray): Camera frame to analyze
        """
        # Look for emergency indicators like fire, traffic hazards, etc.
        emergency_objects = [obj for obj in self.detected_objects 
                             if obj['class'] in self.settings.get('emergency', 'emergency_objects', [])]
        
        # Check for sudden movements or drastic changes in scene
        scene_stability = self.scene_analyzer.assess_scene_stability()
        
        if emergency_objects or scene_stability < self.settings.get('emergency', 'stability_threshold', 0.3):
            self.emergency_data = {
                'emergency_objects': emergency_objects,
                'scene_stability': scene_stability,
                'timestamp': time.time()
            }
        else:
            self.emergency_data = None
    
    def emergency_detected(self):
        """Check if an emergency situation is currently detected.
        
        Returns:
            bool: True if emergency detected, False otherwise
        """
        return self.emergency_data is not None
    
    def get_emergency_data(self):
        """Get current emergency situation data.
        
        Returns:
            dict: Emergency data or None if no emergency
        """
        return self.emergency_data
    
    def release_resources(self):
        """Release all resources used by the vision processor."""
        logger.info("Releasing vision processor resources")
        
        # Stop the capture thread
        self.stop_capture = True
        if self.capture_thread:
            self.capture_thread.join(timeout=1.0)
        
        # Release the camera
        with self.camera_lock:
            if self.camera:
                self.camera.release()
                self.camera = None
        
        # Clear buffers
        self.frame_buffer.clear()

    def load_models(self):
        """Load the required ML models"""
        try:
            self.object_detector = ObjectDetector()
            self.scene_analyzer = SceneAnalyzer()
            print("Models loaded successfully")
        except Exception as e:
            print(f"Failed to load models: {str(e)}")
            raise

    def detect_objects(self, frame):
        """Detect objects in the frame"""
        if self.object_detector is None:
            raise Exception("Object detector not initialized")
        
        try:
            objects = self.object_detector.detect_objects(frame)
            return objects
        except Exception as e:
            print(f"Error in object detection: {str(e)}")
            return []

    def detect_obstacles(self, frame):
        """Detect potential obstacles in the frame"""
        if self.object_detector is None:
            raise Exception("Object detector not initialized")
        
        try:
            obstacles = self.object_detector.classify_obstacles(frame)
            return obstacles
        except Exception as e:
            print(f"Error in obstacle detection: {str(e)}")
            return []

    def analyze_environment(self, frame):
        """Analyze the environment and provide scene description"""
        if self.scene_analyzer is None:
            raise Exception("Scene analyzer not initialized")
        
        try:
            scene_description = self.scene_analyzer.describe_scene(frame)
            return scene_description
        except Exception as e:
            print(f"Error in scene analysis: {str(e)}")
            return "Unable to analyze scene"

    def read_text(self, frame):
        """Perform OCR on the frame to read text"""
        try:
            # Convert to grayscale
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # Apply thresholding
            _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            
            # TODO: Implement OCR using Tesseract or other OCR library
            # For now, return empty string
            return ""
            
        except Exception as e:
            print(f"Error in text reading: {str(e)}")
            return ""

    def preprocess_frame(self, frame):
        """Preprocess the frame for better detection"""
        try:
            # Resize frame if needed
            frame = cv2.resize(frame, (640, 480))
            
            # Apply some basic image enhancement
            frame = cv2.GaussianBlur(frame, (5, 5), 0)
            
            return frame
        except Exception as e:
            print(f"Error in frame preprocessing: {str(e)}")
            return frame