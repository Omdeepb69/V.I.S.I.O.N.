"""
Navigation System - Provides navigation assistance and route planning
"""
import logging
import time
import numpy as np
from collections import deque

from models.environment_mapper import EnvironmentMapper

# Set up logging
logger = logging.getLogger(__name__)

class NavigationSystem:
    """Navigation assistance and route planning system."""
    
    def __init__(self):
        self.environment_mapper = EnvironmentMapper()
        self.current_position = None
        self.destination = None
        self.obstacles = []
        self.landmarks = []
        self.user_profile = {}

    def update_environment(self, objects, obstacles):
        """Update the current environment state"""
        self.obstacles = obstacles
        self.environment_mapper.update_map(objects, obstacles)
        self._identify_landmarks(objects)

    def suggest_path(self, obstacles):
        """Suggest an optimal path based on current obstacles"""
        if not self.destination:
            return "Please set a destination first."
        
        try:
            # Calculate path considering obstacles
            path = self._calculate_path(obstacles)
            
            if not path:
                return "Unable to find a clear path to the destination."
            
            # Generate guidance based on the path
            guidance = self._generate_path_guidance(path)
            return guidance
            
        except Exception as e:
            print(f"Error in path suggestion: {str(e)}")
            return "I'm having trouble suggesting a path at the moment."

    def _calculate_path(self, obstacles):
        """Calculate an optimal path avoiding obstacles"""
        # TODO: Implement path planning algorithm (e.g., A* or RRT)
        # For now, return a simple path
        return []

    def _generate_path_guidance(self, path):
        """Generate verbal guidance for the path"""
        if not path:
            return "No path available."
        
        # TODO: Implement more sophisticated guidance generation
        return "Please proceed straight ahead."

    def _identify_landmarks(self, objects):
        """Identify useful landmarks in the environment"""
        self.landmarks = []
        for obj in objects:
            if self._is_landmark(obj):
                self.landmarks.append(obj)

    def _is_landmark(self, obj):
        """Determine if an object is a useful landmark"""
        # TODO: Implement more sophisticated landmark identification
        landmark_types = ['door', 'elevator', 'stairs', 'exit']
        return obj.get('type', '').lower() in landmark_types

    def set_destination(self, destination):
        """Set the navigation destination"""
        self.destination = destination
        return f"Destination set to {destination}"

    def update_user_profile(self, preferences):
        """Update user navigation preferences"""
        self.user_profile.update(preferences)
        return "Navigation preferences updated"

    def get_current_location(self):
        """Get the current location description"""
        if not self.current_position:
            return "Current position unknown"
        
        # TODO: Implement more sophisticated location description
        return "You are at your current position"

    def estimate_distance(self, target):
        """Estimate distance to a target"""
        # TODO: Implement distance estimation
        return "Distance estimation not available"

    def update_environment(self, environment_data):
        """Update environment map with new sensor data.
        
        Args:
            environment_data (dict): Environment data from vision processor
        """
        try:
            # Update the environment map
            self.environment_mapper.update_map(
                environment_data,
                self.current_position,
                self.current_orientation
            )
            
            # Try to recognize familiar location
            location = self.environment_mapper.recognize_familiar_location()
            if location:
                self.current_position = location['position']
                self.current_orientation = location['orientation']
                logger.info(f"Recognized familiar location: {location['name']}")
            
            # Update position based on visual odometry if implemented
            movement = self.environment_mapper.estimate_movement()
            if movement and self.current_position:
                self.current_position = {
                    'x': self.current_position['x'] + movement['delta_x'],
                    'y': self.current_position['y'] + movement['delta_y'],
                    'z': self.current_position['z'] + movement['delta_z']
                }
                self.current_orientation = movement['orientation']
                
        except Exception as e:
            logger.error(f"Error updating environment: {str(e)}")
    
    def _enhance_path_with_landmarks(self, path):
        """Add landmarks and human-readable directions to path.
        
        Args:
            path (list): Raw path points
            
        Returns:
            list: Enhanced path with landmarks and directions
        """
        enhanced_path = []
        
        for i in range(len(path) - 1):
            # Calculate direction and distance
            start = path[i]
            end = path[i + 1]
            
            direction = self._calculate_direction(start, end)
            distance = self._calculate_distance(start, end)
            
            # Find nearby landmarks
            landmarks = self.environment_mapper.find_nearby_landmarks(end, 5.0)
            
            step = {
                'start': start,
                'end': end,
                'direction': direction,
                'distance': round(distance, 1)
            }
            
            # Add landmark if available and relevant
            if landmarks and self.user_profile['landmark_preference']:
                nearest_landmark = landmarks[0]
                step['landmark'] = nearest_landmark['name']
                step['landmark_position'] = nearest_landmark['position']
            
            enhanced_path.append(step)
        
        return enhanced_path
    
    def _calculate_direction(self, start, end):
        """Calculate human-readable direction between two points.
        
        Args:
            start (dict): Starting point with x, y coordinates
            end (dict): Ending point with x, y coordinates
            
        Returns:
            str: Direction as text (north, northeast, east, etc.)
        """
        # Calculate angle
        dx = end['x'] - start['x']
        dy = end['y'] - start['y']
        angle = np.degrees(np.arctan2(dy, dx))
        
        # Convert angle to direction
        directions = [
            "east", "northeast", "north", "northwest",
            "west", "southwest", "south", "southeast"
        ]
        
        # Normalize angle to 0-360
        angle = (angle + 360) % 360
        
        # Convert angle to direction index
        index = round(angle / 45) % 8
        
        return directions[index]
    
    def _calculate_distance(self, start, end):
        """Calculate distance between two points.
        
        Args:
            start (dict): Starting point with x, y coordinates
            end (dict): Ending point with x, y coordinates
            
        Returns:
            float: Distance in meters
        """
        return np.sqrt((end['x'] - start['x'])**2 + (end['y'] - start['y'])**2)
    
    def identify_landmarks(self):
        """Detect landmarks useful for orientation.
        
        Returns:
            list: List of landmarks with positions and descriptions
        """
        try:
            # Get all landmarks from the mapper
            all_landmarks = self.environment_mapper.get_all_landmarks()
            
            # Sort by distance if we know current position
            if self.current_position:
                all_landmarks = sorted(
                    all_landmarks,
                    key=lambda x: self._calculate_distance(self.current_position, x['position'])
                )
            
            return all_landmarks
            
        except Exception as e:
            logger.error(f"Error identifying landmarks: {str(e)}")
            return []
    
    def get_current_position(self):
        """Get current position if available.
        
        Returns:
            dict: Current position or None if unknown
        """
        return self.current_position
    
    def set_current_position(self, position, source="manual"):
        """Set current position explicitly.
        
        Args:
            position (dict): Position with x, y, z coordinates
            source (str): Source of the position data
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            self.current_position = position
            logger.info(f"Current position set from {source}")
            return True
            
        except Exception as e:
            logger.error(f"Error setting current position: {str(e)}")
            return False
    
    def get_next_navigation_instruction(self):
        """Get the next navigation instruction based on current path.
        
        Returns:
            str: Navigation instruction or None if not available
        """
        if not self.path or not self.current_position:
            return None
            
        # Find the next path segment
        for i, step in enumerate(self.path):
            # Check if we're close to the start of this segment
            dist_to_start = self._calculate_distance(self.current_position, step['start'])
            
            if dist_to_start < 2.0:  # Within 2 meters of the start point
                direction = step['direction']
                distance = step['distance']
                
                instruction = f"Go {direction} for {distance} meters"
                
                # Add landmark if available
                if 'landmark' in step:
                    instruction += f" until you reach {step['landmark']}"
                
                return instruction
        
        return "Continue following the current path."
    
    def reset_navigation(self):
        """Reset navigation state."""
        self.destination = None
        self.path = None