# V.I.S.I.O.N. - Complete User Guide

## System Requirements

- **Operating System**: Windows 10/11, macOS, or Linux
- **Python**: Version 3.8 or higher
- **Hardware**:
  - Webcam or external camera
  - Microphone
  - Speakers or headphones
  - Minimum 4GB RAM
  - 2GB free disk space

## Installation Guide

### 1. Clone the Repository
```bash
git clone https://github.com/Omdeepb69/V.I.S.I.O.N..git
cd V.I.S.I.O.N.
```

### 2. Set Up Virtual Environment
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Initialize Configuration
```bash
python web/app.py
```
This will create necessary configuration files in the `config` directory.

## Configuration Guide

### 1. Web Interface Setup
1. Start the web interface:
   ```bash
   python web/app.py
   ```
2. Open your browser and go to `http://localhost:5000`

### 2. Basic Configuration
In the web interface:

1. **Camera Settings**
   - Set your camera device ID (usually 0 for built-in webcam)
   - Configure resolution (recommended: 640x480)
   - Set FPS (recommended: 30)

2. **Speech Settings**
   - Adjust speech rate (default: 150)
   - Set volume level (0.0 to 1.0)
   - Select preferred language

3. **Navigation Settings**
   - Set map resolution (default: 0.1)
   - Configure map size (default: 100)
   - Adjust obstacle threshold (default: 0.5)

4. **Privacy Settings**
   - Enable/disable privacy mode
   - Configure anonymization settings

### 3. User Profile Setup
1. Go to the "Users" tab
2. Create a new user profile:
   - Enter a unique user ID
   - Set audio volume preferences
   - Configure speech rate
   - Set obstacle alert distance

3. Add familiar locations:
   - Click "Add Location"
   - Enter location name
   - The system will learn the location over time

4. Configure emergency contacts:
   - Go to the "Emergency" tab
   - Add emergency contacts with name, phone, and email
   - Set emergency cooldown period
   - Configure monitoring duration

## Usage Guide

### 1. Starting the System
```bash
python main.py
```

### 2. Voice Commands
The system responds to the following voice commands:

- **Navigation Commands**
  - "Where am I?" - Get current location information
  - "What's in front of me?" - Describe immediate surroundings
  - "Guide me to [location]" - Start navigation to a familiar location
  - "Stop navigation" - End current navigation

- **Environment Commands**
  - "Scan surroundings" - Perform detailed environment analysis
  - "Describe scene" - Get a detailed description of the current scene
  - "Read text" - Read any visible text in the environment
  - "Find person" - Locate and identify people in the vicinity

- **System Commands**
  - "Adjust volume [level]" - Change audio volume (0-100)
  - "Change language [language]" - Switch to a different language
  - "Privacy mode [on/off]" - Toggle privacy settings
  - "Emergency help" - Activate emergency protocols

### 3. Understanding Audio Feedback

- **Directional Cues**
  - Left/right audio panning indicates direction
  - Volume changes indicate distance
  - Different tones for different types of obstacles

- **Obstacle Alerts**
  - High-pitched tone: Immediate danger
  - Medium-pitched tone: Warning
  - Low-pitched tone: Information

- **Navigation Guidance**
  - Continuous audio feedback while moving
  - Distance updates every few seconds
  - Turn indicators before reaching intersections

### 4. Emergency Features

1. **Automatic Emergency Detection**
   - System detects potential dangers
   - Provides immediate audio warnings
   - Suggests safe actions

2. **Manual Emergency Activation**
   - Say "Emergency help" to activate
   - System will:
     - Alert emergency contacts
     - Provide guidance
     - Monitor the situation

3. **Emergency Protocols**
   - Immediate danger: System provides clear instructions
   - Medical emergency: Guides to safe location
   - Navigation emergency: Provides alternative routes

## Troubleshooting

### Common Issues

1. **Camera Not Detected**
   - Check camera connection
   - Verify correct device ID in settings
   - Ensure camera permissions are granted

2. **Audio Issues**
   - Check microphone and speaker connections
   - Verify audio device settings
   - Adjust volume levels in system settings

3. **Navigation Problems**
   - Ensure sufficient lighting
   - Check for camera obstructions
   - Verify location permissions

### Error Messages

- **"Camera initialization failed"**
  - Solution: Check camera connection and settings

- **"Audio device not found"**
  - Solution: Verify audio device connections

- **"Location not recognized"**
  - Solution: Add location to familiar locations

## Maintenance

### Regular Tasks
1. Update system settings as needed
2. Add new familiar locations
3. Update emergency contacts
4. Review and adjust user preferences

### System Updates
1. Pull latest changes from repository
2. Update dependencies:
   ```bash
   pip install -r requirements.txt --upgrade
   ```
3. Restart the system

## Support

For additional help:
1. Check the project documentation
2. Open an issue on GitHub
3. Contact the development team

## Safety Guidelines

1. Always test the system in safe environments first
2. Keep emergency contacts updated
3. Regularly verify system functionality
4. Have backup navigation methods available
5. Maintain system updates for security

Remember: The AI Vision Assistant is designed to assist, not replace, human judgment and common sense. 