import numpy as np

class EnvironmentMapper:
    def __init__(self):
        self.map = None
        self.map_resolution = 0.1  # meters per pixel
        self.map_size = 100  # pixels
        self.known_locations = {}
        self.landmarks = []

    def update_map(self, objects, obstacles):
        """Update the environment map with new data"""
        try:
            # Initialize map if not exists
            if self.map is None:
                self.map = np.zeros((self.map_size, self.map_size), dtype=np.float32)
            
            # Update map with new objects and obstacles
            self._update_objects(objects)
            self._update_obstacles(obstacles)
            
            # Update landmarks
            self._update_landmarks(objects)
            
            return True
        except Exception as e:
            print(f"Error updating map: {str(e)}")
            return False

    def _update_objects(self, objects):
        """Update the map with detected objects"""
        try:
            for obj in objects:
                # Convert object position to map coordinates
                map_x, map_y = self._world_to_map_coordinates(
                    obj.get('position_x', 0),
                    obj.get('position_y', 0)
                )
                
                # Update map cell
                if 0 <= map_x < self.map_size and 0 <= map_y < self.map_size:
                    self.map[map_y, map_x] = 0.5  # Mark as occupied
        except Exception as e:
            print(f"Error updating objects: {str(e)}")

    def _update_obstacles(self, obstacles):
        """Update the map with detected obstacles"""
        try:
            for obstacle in obstacles:
                # Convert obstacle position to map coordinates
                map_x, map_y = self._world_to_map_coordinates(
                    obstacle.get('position_x', 0),
                    obstacle.get('position_y', 0)
                )
                
                # Update map cell
                if 0 <= map_x < self.map_size and 0 <= map_y < self.map_size:
                    self.map[map_y, map_x] = 1.0  # Mark as obstacle
        except Exception as e:
            print(f"Error updating obstacles: {str(e)}")

    def _update_landmarks(self, objects):
        """Update the list of landmarks"""
        try:
            for obj in objects:
                if self._is_landmark(obj):
                    landmark = {
                        'type': obj.get('class', 'unknown'),
                        'position': (obj.get('position_x', 0), obj.get('position_y', 0)),
                        'confidence': obj.get('confidence', 0.0)
                    }
                    self.landmarks.append(landmark)
        except Exception as e:
            print(f"Error updating landmarks: {str(e)}")

    def _is_landmark(self, obj):
        """Determine if an object is a useful landmark"""
        landmark_types = ['door', 'elevator', 'stairs', 'exit', 'sign']
        return obj.get('class', '').lower() in landmark_types

    def _world_to_map_coordinates(self, world_x, world_y):
        """Convert world coordinates to map coordinates"""
        map_x = int(world_x / self.map_resolution) + self.map_size // 2
        map_y = int(world_y / self.map_resolution) + self.map_size // 2
        return map_x, map_y

    def _map_to_world_coordinates(self, map_x, map_y):
        """Convert map coordinates to world coordinates"""
        world_x = (map_x - self.map_size // 2) * self.map_resolution
        world_y = (map_y - self.map_size // 2) * self.map_resolution
        return world_x, world_y

    def recognize_familiar_location(self, current_objects):
        """Identify if current location matches a previously visited location"""
        try:
            if not self.known_locations:
                return None
            
            # Compare current objects with known locations
            for location_name, location_data in self.known_locations.items():
                similarity = self._calculate_location_similarity(
                    current_objects,
                    location_data['objects']
                )
                
                if similarity > 0.8:  # Threshold for recognition
                    return location_name
            
            return None
        except Exception as e:
            print(f"Error recognizing location: {str(e)}")
            return None

    def _calculate_location_similarity(self, objects1, objects2):
        """Calculate similarity between two sets of objects"""
        try:
            if not objects1 or not objects2:
                return 0.0
            
            # Count matching object types
            types1 = set(obj.get('class', '') for obj in objects1)
            types2 = set(obj.get('class', '') for obj in objects2)
            
            matching_types = len(types1.intersection(types2))
            total_types = len(types1.union(types2))
            
            return matching_types / total_types if total_types > 0 else 0.0
        except Exception as e:
            print(f"Error calculating location similarity: {str(e)}")
            return 0.0

    def save_location(self, location_name, objects):
        """Save current location as a known location"""
        try:
            self.known_locations[location_name] = {
                'objects': objects,
                'timestamp': np.datetime64('now')
            }
            return True
        except Exception as e:
            print(f"Error saving location: {str(e)}")
            return False 