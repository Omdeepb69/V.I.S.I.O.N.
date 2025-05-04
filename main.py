#!/usr/bin/env python3
"""
AI Vision Assistant - Main Application Entry Point
"""
import os
import time
import argparse
import logging
from threading import Thread

import cv2
import numpy as np
from core.vision_processor import VisionProcessor
from core.assistant_agent import AssistantAgent
from core.navigation import NavigationSystem
from utils.speech import SpeechProcessor
from utils.spatial_audio import SpatialAudioGenerator
from utils.emergency_handler import EmergencyHandler
from config.settings import Settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("vision_assistant.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class AIVisionAssistant:
    """Main class that coordinates all components of the AI Vision Assistant."""
    
    def __init__(self):
        """Initialize the Vision Assistant system."""
        self.settings = Settings()
        self.settings.load_config()
        
        logger.info("Initializing AI Vision Assistant...")
        
        # Initialize core components
        self.vision_processor = VisionProcessor()
        self.assistant_agent = AssistantAgent()
        self.navigation = NavigationSystem()
        self.speech = SpeechProcessor()
        self.spatial_audio = SpatialAudioGenerator()
        self.emergency_handler = EmergencyHandler()
        
        # Control flags
        self.running = False
        self.camera = None
        
    def initialize_system(self):
        """Initialize all components of the system"""
        try:
            # Initialize camera
            self.camera = cv2.VideoCapture(0)
            if not self.camera.isOpened():
                raise Exception("Failed to open camera")

            # Initialize speech recognition
            self.speech.initialize()

            # Load models
            self.vision_processor.load_models()

            logger.info("System initialized successfully")
            return True
        except Exception as e:
            logger.error(f"Initialization failed: {str(e)}")
            return False
    
    def process_frame(self, frame):
        """Process a single camera frame"""
        # Detect objects and obstacles
        objects = self.vision_processor.detect_objects(frame)
        obstacles = self.vision_processor.detect_obstacles(frame)
        
        # Analyze scene
        scene_description = self.vision_processor.analyze_environment(frame)
        
        # Update navigation system
        self.navigation.update_environment(objects, obstacles)
        
        return objects, obstacles, scene_description
    
    def run_assistant(self):
        """Main loop for processing camera input and providing feedback"""
        self.running = True
        
        try:
            while self.running:
                # Capture frame
                ret, frame = self.camera.read()
                if not ret:
                    logger.error("Failed to capture frame")
                    continue

                # Process frame
                objects, obstacles, scene_description = self.process_frame(frame)

                # Check for emergency situations
                if self.emergency_handler.assess_danger_level(obstacles):
                    self.emergency_handler.handle_emergency()
                    continue

                # Generate navigation guidance
                guidance = self.navigation.suggest_path(obstacles)
                
                # Convert guidance to speech
                self.speech.speak(guidance)
                
                # Generate spatial audio cues
                self.spatial_audio.create_direction_cue(guidance)

                # Check for user voice commands
                if self.speech.is_listening():
                    command = self.speech.listen()
                    if command:
                        response = self.assistant_agent.process_user_query(command)
                        self.speech.speak(response)

        except KeyboardInterrupt:
            logger.info("Shutting down...")
        finally:
            self.cleanup()
    
    def cleanup(self):
        """Clean up resources"""
        self.running = False
        if hasattr(self, 'camera'):
            self.camera.release()
        cv2.destroyAllWindows()
        self.speech.cleanup()

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="AI Vision Assistant for the Visually Impaired")
    parser.add_argument("--camera", type=int, default=0, help="Camera device ID (default: 0)")
    parser.add_argument("--config", type=str, default="config/config.json", help="Path to configuration file")
    return parser.parse_args()

def main():
    """Main function to start the AI Vision Assistant."""
    args = parse_arguments()
    
    assistant = AIVisionAssistant()
    assistant.camera = cv2.VideoCapture(args.camera)
    
    # Set config path if provided
    if args.config:
        assistant.settings.config_path = args.config
    
    # Initialize system components
    if assistant.initialize_system():
        # Start the main processing loop
        assistant.run_assistant()
    else:
        logger.error("Failed to initialize Vision Assistant. Exiting.")
        return 1
    
    return 0

if __name__ == "__main__":
    exit_code = main()
    exit(exit_code)