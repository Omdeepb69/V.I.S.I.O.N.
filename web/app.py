from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import os
from datetime import datetime
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

# Configuration paths
CONFIG_DIR = "config"
USER_PROFILES_FILE = os.path.join(CONFIG_DIR, "user_profiles.json")
SETTINGS_FILE = os.path.join(CONFIG_DIR, "settings.json")

@app.route('/')
def index():
    """Render the main configuration interface"""
    return render_template('index.html')

@app.route('/api/settings', methods=['GET'])
def get_settings():
    """Get current application settings"""
    try:
        with open(SETTINGS_FILE, 'r') as f:
            settings = json.load(f)
        return jsonify(settings)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/settings', methods=['POST'])
def update_settings():
    """Update application settings"""
    try:
        settings = request.json
        with open(SETTINGS_FILE, 'w') as f:
            json.dump(settings, f, indent=4)
        return jsonify({"status": "success"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/users', methods=['GET'])
def get_users():
    """Get all user profiles"""
    try:
        with open(USER_PROFILES_FILE, 'r') as f:
            users = json.load(f)
        return jsonify(users)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/users/<user_id>', methods=['GET'])
def get_user(user_id):
    """Get specific user profile"""
    try:
        with open(USER_PROFILES_FILE, 'r') as f:
            users = json.load(f)
        if user_id in users:
            return jsonify(users[user_id])
        return jsonify({"error": "User not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/users/<user_id>', methods=['POST'])
def update_user(user_id):
    """Update user profile"""
    try:
        with open(USER_PROFILES_FILE, 'r') as f:
            users = json.load(f)
        
        if user_id not in users:
            users[user_id] = {
                "preferences": {},
                "familiar_locations": {},
                "navigation_history": [],
                "feedback_scores": [],
                "created_at": datetime.now().isoformat()
            }
        
        users[user_id].update(request.json)
        
        with open(USER_PROFILES_FILE, 'w') as f:
            json.dump(users, f, indent=4)
        
        return jsonify({"status": "success"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/users/<user_id>/feedback', methods=['POST'])
def add_feedback(user_id):
    """Add user feedback"""
    try:
        with open(USER_PROFILES_FILE, 'r') as f:
            users = json.load(f)
        
        if user_id not in users:
            return jsonify({"error": "User not found"}), 404
        
        feedback = {
            **request.json,
            "timestamp": datetime.now().isoformat()
        }
        
        if "feedback_scores" not in users[user_id]:
            users[user_id]["feedback_scores"] = []
        
        users[user_id]["feedback_scores"].append(feedback)
        
        with open(USER_PROFILES_FILE, 'w') as f:
            json.dump(users, f, indent=4)
        
        return jsonify({"status": "success"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/users/<user_id>/locations', methods=['GET'])
def get_familiar_locations(user_id):
    """Get user's familiar locations"""
    try:
        with open(USER_PROFILES_FILE, 'r') as f:
            users = json.load(f)
        
        if user_id not in users:
            return jsonify({"error": "User not found"}), 404
        
        return jsonify(users[user_id].get("familiar_locations", {}))
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/users/<user_id>/locations', methods=['POST'])
def add_familiar_location(user_id):
    """Add a familiar location"""
    try:
        with open(USER_PROFILES_FILE, 'r') as f:
            users = json.load(f)
        
        if user_id not in users:
            return jsonify({"error": "User not found"}), 404
        
        location_data = request.json
        location_id = f"loc_{len(users[user_id].get('familiar_locations', {}))}"
        
        if "familiar_locations" not in users[user_id]:
            users[user_id]["familiar_locations"] = {}
        
        users[user_id]["familiar_locations"][location_id] = {
            **location_data,
            "last_visited": datetime.now().isoformat(),
            "visit_count": 1
        }
        
        with open(USER_PROFILES_FILE, 'w') as f:
            json.dump(users, f, indent=4)
        
        return jsonify({"status": "success", "location_id": location_id})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/emergency-contacts', methods=['GET'])
def get_emergency_contacts():
    """Get emergency contacts"""
    try:
        with open(SETTINGS_FILE, 'r') as f:
            settings = json.load(f)
        return jsonify(settings.get("emergency_contacts", []))
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/emergency-contacts', methods=['POST'])
def add_emergency_contact():
    """Add emergency contact"""
    try:
        with open(SETTINGS_FILE, 'r') as f:
            settings = json.load(f)
        
        if "emergency_contacts" not in settings:
            settings["emergency_contacts"] = []
        
        settings["emergency_contacts"].append(request.json)
        
        with open(SETTINGS_FILE, 'w') as f:
            json.dump(settings, f, indent=4)
        
        return jsonify({"status": "success"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # Ensure config directory exists
    os.makedirs(CONFIG_DIR, exist_ok=True)
    
    # Initialize settings file if it doesn't exist
    if not os.path.exists(SETTINGS_FILE):
        default_settings = {
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
            "privacy": {
                "enabled": True,
                "anonymization": True
            }
        }
        with open(SETTINGS_FILE, 'w') as f:
            json.dump(default_settings, f, indent=4)
    
    # Initialize user profiles file if it doesn't exist
    if not os.path.exists(USER_PROFILES_FILE):
        with open(USER_PROFILES_FILE, 'w') as f:
            json.dump({}, f, indent=4)
    
    # Run the Flask app
    app.run(host='0.0.0.0', port=5000, debug=True) 