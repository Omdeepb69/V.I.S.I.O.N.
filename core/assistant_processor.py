"""
Assistant Agent - Central AI agent that coordinates all system responses and actions
"""
import logging
import threading
import time
import queue
import random

# Set up logging
logger = logging.getLogger(__name__)

class AssistantAgent:
    """Main AI assistant coordinator that manages user interactions and system responses."""
    
    def __init__(self, settings, vision_processor, navigation_system, 
                 speech_processor, spatial_audio, emergency_handler):
        """Initialize the Assistant Agent.
        
        Args:
            settings (Settings): Application settings
            vision_processor (VisionProcessor): Vision processing component
            navigation_system (NavigationSystem): Navigation assistance component
            speech_processor (SpeechProcessor): Speech recognition and synthesis
            spatial_audio (SpatialAudioGenerator): Spatial audio feedback generator
            emergency_handler (EmergencyHandler): Emergency situation handler
        """
        self.settings = settings
        self.vision_processor = vision_processor
        self.navigation_system = navigation_system
        self.speech_processor = speech_processor
        self.spatial_audio = spatial_audio
        self.emergency_handler = emergency_handler
        
        # User interaction queue
        self.interaction_queue = queue.Queue()
        
        # User query history
        self.query_history = []
        
        # Interaction state
        self.current_task = None
        self.guidance_active = False
        self.last_obstacle_alert = 0
        self.obstacle_alert_cooldown = settings.get('interaction', 'obstacle_alert_cooldown', 5)
        
        # Start the interaction processing thread
        self.stop_processing = False
        self.processing_thread = threading.Thread(target=self._process_interactions)
        self.processing_thread.daemon = True
        self.processing_thread.start()
        
        logger.info("Assistant agent initialized")
    
    def process_user_query(self, query_text):
        """Process a user query and generate appropriate response.
        
        Args:
            query_text (str): User's spoken query
            
        Returns:
            str: Response to be spoken to the user
        """
        if not query_text or query_text.strip() == "":
            return None
            
        query_text = query_text.lower().strip()
        logger.info(f"Processing user query: '{query_text}'")
        
        # Add to query history
        self.query_history.append({
            'query': query_text,
            'timestamp': time.time()
        })
        
        # Add to interaction queue
        self.interaction_queue.put({
            'type': 'query',
            'text': query_text,
            'timestamp': time.time()
        })
        
        # Return placeholder response (real response will be processed by the thread)
        return "Processing your request..."
    
    def handle_obstacles(self, obstacles):
        """Handle detected obstacles by providing appropriate feedback.
        
        Args:
            obstacles (list): List of detected obstacles
        """
        if not obstacles:
            return
            
        current_time = time.time()
        
        # Check if we should alert about obstacles (avoid too frequent alerts)
        if current_time - self.last_obstacle_alert < self.obstacle_alert_cooldown:
            return
            
        self.last_obstacle_alert = current_time
        
        # Add to interaction queue
        self.interaction_queue.put({
            'type': 'obstacle',
            'obstacles': obstacles,
            'timestamp': current_time
        })
    
    def _process_interactions(self):
        """Background thread to process user interactions and system events."""
        while not self.stop_processing:
            try:
                # Get next interaction with a timeout
                try:
                    interaction = self.interaction_queue.get(timeout=0.5)
                except queue.Empty:
                    continue
                
                # Process based on interaction type
                if interaction['type'] == 'query':
                    self._handle_query(interaction['text'])
                elif interaction['type'] == 'obstacle':
                    self._alert_obstacles(interaction['obstacles'])
                
                # Mark as done
                self.interaction_queue.task_done()
                
            except Exception as e:
            logger.error(f"Error handling emergency: {str(e)}")
            self.speech_processor.speak("Warning! Potential danger detected. Please proceed with caution.", interrupt=True)
    
    def stop(self):
        """Stop the assistant agent and release resources."""
        logger.info("Stopping assistant agent")
        self.stop_processing = True
        if self.processing_thread:
            self.processing_thread.join(timeout=1.0)
    logger.error(f"Error processing interaction: {str(e)}")
                
    def _handle_query(self, query_text):
        """Handle a user query internally.
        
        Args:
            query_text (str): User's query text
        """
        # Handle system commands
        if self._handle_system_command(query_text):
            return
            
        # Handle navigation requests
        if self._is_navigation_request(query_text):
            self._handle_navigation_request(query_text)
            return
            
        # Handle environment questions
        if self._is_environment_question(query_text):
            self._describe_environment()
            return
            
        # Handle reading text
        if self._is_reading_request(query_text):
            self._read_visible_text()
            return
            
        # General queries
        response = self._generate_general_response(query_text)
        self.speech_processor.speak(response)
    
    def _handle_system_command(self, query_text):
        """Handle system-level commands.
        
        Args:
            query_text (str): User's query text
            
        Returns:
            bool: True if handled as a command, False otherwise
        """
        # Check for stop/exit commands
        if any(cmd in query_text for cmd in ["stop", "exit", "quit", "end", "terminate"]):
            self.speech_processor.speak("Stopping the assistant. Goodbye!")
            # Signal to stop the main loop
            self.stop_processing = True
            return True
            
        # Check for pause command
        if any(cmd in query_text for cmd in ["pause", "wait", "hold on"]):
            self.speech_processor.speak("Pausing navigation guidance. Say 'resume' to continue.")
            self.guidance_active = False
            return True
            
        # Check for resume command
        if any(cmd in query_text for cmd in ["resume", "continue", "go on"]):
            self.speech_processor.speak("Resuming navigation guidance.")
            self.guidance_active = True
            return True
            
        return False
    
    def _is_navigation_request(self, query_text):
        """Check if the query is related to navigation.
        
        Args:
            query_text (str): User's query text
            
        Returns:
            bool: True if it's a navigation request
        """
        nav_keywords = [
            "where", "how to get", "take me", "guide me", "directions", "navigate",
            "find", "locate", "go to", "path", "route", "way to"
        ]
        
        return any(keyword in query_text for keyword in nav_keywords)
    
    def _handle_navigation_request(self, query_text):
        """Handle a navigation-related request.
        
        Args:
            query_text (str): User's query text
        """
        # Extract destination from query
        destination = self._extract_destination(query_text)
        
        if not destination:
            self.speech_processor.speak("I'm not sure where you want to go. Could you specify a destination?")
            return
            
        # Generate navigation guidance
        guidance = self.generate_guidance(destination)
        
        if guidance:
            self.speech_processor.speak(guidance['initial_instruction'])
            
            # Activate ongoing guidance
            self.guidance_active = True
            self.current_task = {
                'type': 'navigation',
                'destination': destination,
                'guidance': guidance
            }
        else:
            self.speech_processor.speak(f"I'm sorry, I couldn't find a path to {destination}.")
    
    def _extract_destination(self, query_text):
        """Extract destination from a navigation query.
        
        Args:
            query_text (str): User's query text
            
        Returns:
            str: Extracted destination or None
        """
        # Basic extraction - could be enhanced with NLP
        nav_prefixes = [
            "where is", "how to get to", "take me to", "guide me to", 
            "directions to", "navigate to", "find", "locate", "go to",
            "path to", "route to", "way to"
        ]
        
        for prefix in nav_prefixes:
            if prefix in query_text:
                # Extract text after the prefix
                destination = query_text.split(prefix, 1)[1].strip()
                if destination:
                    return destination
        
        return None
    
    def _is_environment_question(self, query_text):
        """Check if the query is asking about the environment.
        
        Args:
            query_text (str): User's query text
            
        Returns:
            bool: True if it's an environment question
        """
        env_keywords = [
            "what is", "what's", "describe", "tell me", "see", "around",
            "surrounding", "environment", "where am i", "what do you see"
        ]
        
        return any(keyword in query_text for keyword in env_keywords)
    
    def _describe_environment(self):
        """Generate and speak a description of the current environment."""
        # Get environment data
        env_data = self.vision_processor.analyze_environment()
        
        # Build description
        description = "I can see "
        
        # Add scene type
        if env_data['scene_type']:
            description += f"that you're in a {env_data['scene_type']}. "
        
        # Add objects
        if env_data['objects']:
            obj_counts = {}
            for obj in env_data['objects']:
                obj_class = obj['class']
                obj_counts[obj_class] = obj_counts.get(obj_class, 0) + 1
            
            obj_descriptions = []
            for obj_class, count in obj_counts.items():
                if count > 1:
                    obj_descriptions.append(f"{count} {obj_class}s")
                else:
                    obj_descriptions.append(f"a {obj_class}")
            
            if obj_descriptions:
                description += "I can see " + ", ".join(obj_descriptions)
                description += ". "
        
        # Add obstacles
        if env_data['obstacles']:
            obstacle_positions = []
            for obstacle in env_data['obstacles']:
                position = self._describe_position(obstacle['position'])
                obstacle_positions.append(f"{obstacle['class']} {position}")
            
            description += "Be careful of " + ", ".join(obstacle_positions)
            description += ". "
        
        # Use the full description if available
        if env_data['description']:
            description = env_data['description']
        
        # Speak the description
        self.speech_processor.speak(description)
    
    def _describe_position(self, position):
        """Convert a position dict to a human-readable description.
        
        Args:
            position (dict): Position information with x, y values
            
        Returns:
            str: Position description
        """
        # Center of the frame is (0.5, 0.5)
        x, y = position['x'], position['y']
        
        # Horizontal position
        if x < 0.33:
            h_pos = "to your left"
        elif x > 0.66:
            h_pos = "to your right"
        else:
            h_pos = "in front of you"
        
        # Distance (based on y-position in the frame)
        if y < 0.33:
            distance = "far"
        elif y < 0.66:
            distance = "at medium distance"
        else:
            distance = "very close"
        
        return f"{h_pos}, {distance}"
    
    def _is_reading_request(self, query_text):
        """Check if the query is asking to read text.
        
        Args:
            query_text (str): User's query text
            
        Returns:
            bool: True if it's a reading request
        """
        read_keywords = [
            "read", "text", "what does it say", "what is written", 
            "what's written", "what does this say"
        ]
        
        return any(keyword in query_text for keyword in read_keywords)
    
    def _read_visible_text(self):
        """Read any visible text in the current frame."""
        # Get the most recent frame
        frame = self.vision_processor.get_frame()
        if frame is None:
            self.speech_processor.speak("I can't access the camera to read text.")
            return
        
        # Extract text
        text = self.vision_processor.read_text(frame)
        
        if text and text.strip():
            self.speech_processor.speak(f"I can see the following text: {text}")
        else:
            self.speech_processor.speak("I don't see any readable text in view.")
    
    def _generate_general_response(self, query_text):
        """Generate a response for general queries.
        
        Args:
            query_text (str): User's query text
            
        Returns:
            str: Generated response
        """
        # Simple responses for common queries
        responses = {
            "help": "I can help you navigate, describe your surroundings, read text, and answer questions. Just ask me what you need.",
            "hello": "Hello! I'm your AI vision assistant. How can I help you today?",
            "hi": "Hi there! I'm here to assist you. What would you like to know?",
            "thank": "You're welcome! I'm happy to help.",
            "what can you do": "I can describe your surroundings, help you navigate, read text, and answer your questions about the environment.",
            "who are you": "I'm your AI vision assistant, designed to help visually impaired users understand their environment and navigate safely."
        }
        
        # Check for matches
        for key, response in responses.items():
            if key in query_text:
                return response
        
        # Default response
        return "I'm not sure how to answer that. You can ask me to describe what I see, help you navigate, or read text for you."
    
    def generate_guidance(self, destination):
        """Create navigation instructions for a destination.
        
        Args:
            destination (str): Target destination
            
        Returns:
            dict: Guidance information or None if not possible
        """
        try:
            # Request path from navigation system
            path = self.navigation_system.suggest_path(destination)
            
            if not path:
                return None
                
            # Generate initial instruction
            initial_direction = path[0]['direction']
            initial_distance = path[0]['distance']
            
            initial_instruction = f"To reach {destination}, start by going {initial_direction} for about {initial_distance} meters."
            
            # Add information about the first landmark if available
            if len(path) > 1 and 'landmark' in path[1]:
                initial_instruction += f" You'll see {path[1]['landmark']} ahead."
            
            return {
                'path': path,
                'destination': destination,
                'initial_instruction': initial_instruction,
                'current_step': 0
            }
            
        except Exception as e:
            logger.error(f"Error generating guidance: {str(e)}")
            return None
    
    def handle_emergency(self, emergency_data):
        """Handle an emergency situation.
        
        Args:
            emergency_data (dict): Emergency situation data
        """
        try:
            # Let the emergency handler deal with the situation
            self.emergency_handler.assess_danger_level(emergency_data)
            
            # Get emergency guidance
            guidance = self.emergency_handler.provide_emergency_guidance()
            
            # Interrupt normal operation
            self.current_task = {
                'type': 'emergency',
                'data': emergency_data,
                'guidance': guidance
            }
            
            # Alert the user with highest priority
            self.speech_processor.speak(guidance, interrupt=True)
            
            # Generate spatial audio alert
            self.spatial_audio.generate_emergency_alert()
            
        except Exception as e: