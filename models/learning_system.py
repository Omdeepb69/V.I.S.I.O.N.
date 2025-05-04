import numpy as np
import json
import os
from datetime import datetime

class LearningSystem:
    def __init__(self):
        self.user_profiles = {}
        self.feedback_history = []
        self.learning_rate = 0.1
        self.profile_file = "user_profiles.json"
        self._load_profiles()

    def _load_profiles(self):
        """Load user profiles from file"""
        try:
            if os.path.exists(self.profile_file):
                with open(self.profile_file, 'r') as f:
                    self.user_profiles = json.load(f)
        except Exception as e:
            print(f"Error loading user profiles: {str(e)}")
            self.user_profiles = {}

    def _save_profiles(self):
        """Save user profiles to file"""
        try:
            with open(self.profile_file, 'w') as f:
                json.dump(self.user_profiles, f, indent=4)
        except Exception as e:
            print(f"Error saving user profiles: {str(e)}")

    def create_user_profile(self, user_id):
        """Create a new user profile"""
        if user_id not in self.user_profiles:
            self.user_profiles[user_id] = {
                "preferences": {
                    "audio_volume": 0.7,
                    "speech_rate": 150,
                    "obstacle_alert_distance": 2.0,
                    "preferred_landmarks": []
                },
                "familiar_locations": {},
                "navigation_history": [],
                "feedback_scores": [],
                "created_at": datetime.now().isoformat()
            }
            self._save_profiles()
            return True
        return False

    def update_preferences(self, user_id, preferences):
        """Update user preferences"""
        if user_id in self.user_profiles:
            self.user_profiles[user_id]["preferences"].update(preferences)
            self._save_profiles()
            return True
        return False

    def add_familiar_location(self, user_id, location_data):
        """Add a familiar location to user profile"""
        if user_id in self.user_profiles:
            location_id = f"loc_{len(self.user_profiles[user_id]['familiar_locations'])}"
            self.user_profiles[user_id]["familiar_locations"][location_id] = {
                **location_data,
                "last_visited": datetime.now().isoformat(),
                "visit_count": 1
            }
            self._save_profiles()
            return True
        return False

    def update_familiar_location(self, user_id, location_id, location_data):
        """Update a familiar location"""
        if user_id in self.user_profiles and location_id in self.user_profiles[user_id]["familiar_locations"]:
            self.user_profiles[user_id]["familiar_locations"][location_id].update(location_data)
            self.user_profiles[user_id]["familiar_locations"][location_id]["visit_count"] += 1
            self.user_profiles[user_id]["familiar_locations"][location_id]["last_visited"] = datetime.now().isoformat()
            self._save_profiles()
            return True
        return False

    def add_feedback(self, user_id, feedback_data):
        """Add user feedback to improve the system"""
        if user_id in self.user_profiles:
            feedback = {
                **feedback_data,
                "timestamp": datetime.now().isoformat()
            }
            self.user_profiles[user_id]["feedback_scores"].append(feedback)
            
            # Update preferences based on feedback
            self._update_preferences_from_feedback(user_id, feedback)
            
            self._save_profiles()
            return True
        return False

    def _update_preferences_from_feedback(self, user_id, feedback):
        """Update user preferences based on feedback"""
        if "preference_scores" in feedback:
            current_prefs = self.user_profiles[user_id]["preferences"]
            for pref, score in feedback["preference_scores"].items():
                if pref in current_prefs:
                    # Update preference using learning rate
                    current_prefs[pref] = (1 - self.learning_rate) * current_prefs[pref] + \
                                        self.learning_rate * score

    def get_user_preferences(self, user_id):
        """Get user preferences"""
        return self.user_profiles.get(user_id, {}).get("preferences", {})

    def get_familiar_locations(self, user_id):
        """Get familiar locations for a user"""
        return self.user_profiles.get(user_id, {}).get("familiar_locations", {})

    def recognize_location(self, user_id, current_location_data):
        """Recognize if current location matches a familiar location"""
        familiar_locations = self.get_familiar_locations(user_id)
        
        for loc_id, loc_data in familiar_locations.items():
            similarity = self._calculate_location_similarity(
                current_location_data,
                loc_data
            )
            
            if similarity > 0.8:  # Threshold for recognition
                return loc_id, loc_data
        
        return None, None

    def _calculate_location_similarity(self, loc1, loc2):
        """Calculate similarity between two locations"""
        # Simple feature comparison
        features1 = set(loc1.get("features", []))
        features2 = set(loc2.get("features", []))
        
        if not features1 or not features2:
            return 0.0
            
        intersection = len(features1.intersection(features2))
        union = len(features1.union(features2))
        
        return intersection / union if union > 0 else 0.0

    def get_navigation_history(self, user_id):
        """Get navigation history for a user"""
        return self.user_profiles.get(user_id, {}).get("navigation_history", [])

    def add_navigation_step(self, user_id, step_data):
        """Add a navigation step to history"""
        if user_id in self.user_profiles:
            step = {
                **step_data,
                "timestamp": datetime.now().isoformat()
            }
            self.user_profiles[user_id]["navigation_history"].append(step)
            self._save_profiles()
            return True
        return False 