import json
import os

class Settings:
    def __init__(self):
        self.config_file = "config.json"
        self.default_settings = {
            "camera": {
                "device_id": 0,
                "resolution": [640, 480],
                "fps": 30
            },
            "speech": {
                "rate": 150,
                "volume": 0.9,
                "language": "en-US"
            },
            "audio": {
                "sample_rate": 44100,
                "volume": 0.5,
                "duration": 0.5
            },
            "navigation": {
                "map_resolution": 0.1,
                "map_size": 100,
                "obstacle_threshold": 0.5
            },
            "emergency": {
                "cooldown": 60,
                "contacts": [],
                "monitoring_duration": 30
            },
            "models": {
                "object_detector": {
                    "confidence_threshold": 0.5,
                    "nms_threshold": 0.4
                },
                "scene_analyzer": {
                    "environment_types": ["indoor", "outdoor", "mixed"],
                    "scene_categories": ["room", "corridor", "street", "park", "building", "unknown"]
                }
            }
        }
        self.settings = self._load_settings()

    def _load_settings(self):
        """Load settings from config file or use defaults"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    loaded_settings = json.load(f)
                    # Merge with defaults to ensure all settings exist
                    return self._merge_settings(self.default_settings, loaded_settings)
            else:
                # Save defaults if no config file exists
                self._save_settings(self.default_settings)
                return self.default_settings
        except Exception as e:
            print(f"Error loading settings: {str(e)}")
            return self.default_settings

    def _save_settings(self, settings):
        """Save settings to config file"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(settings, f, indent=4)
            return True
        except Exception as e:
            print(f"Error saving settings: {str(e)}")
            return False

    def _merge_settings(self, default, loaded):
        """Merge loaded settings with defaults"""
        merged = default.copy()
        for key, value in loaded.items():
            if key in merged and isinstance(merged[key], dict) and isinstance(value, dict):
                merged[key] = self._merge_settings(merged[key], value)
            else:
                merged[key] = value
        return merged

    def get(self, section, key, default=None):
        """Get a setting value"""
        try:
            return self.settings.get(section, {}).get(key, default)
        except Exception as e:
            print(f"Error getting setting: {str(e)}")
            return default

    def set(self, section, key, value):
        """Set a setting value"""
        try:
            if section not in self.settings:
                self.settings[section] = {}
            self.settings[section][key] = value
            return self._save_settings(self.settings)
        except Exception as e:
            print(f"Error setting value: {str(e)}")
            return False

    def update_section(self, section, values):
        """Update an entire section of settings"""
        try:
            if section not in self.settings:
                self.settings[section] = {}
            self.settings[section].update(values)
            return self._save_settings(self.settings)
        except Exception as e:
            print(f"Error updating section: {str(e)}")
            return False

    def reset_to_defaults(self):
        """Reset all settings to defaults"""
        try:
            self.settings = self.default_settings.copy()
            return self._save_settings(self.settings)
        except Exception as e:
            print(f"Error resetting settings: {str(e)}")
            return False 