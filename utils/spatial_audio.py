import numpy as np
import sounddevice as sd
import threading
import queue

class SpatialAudioGenerator:
    def __init__(self):
        self.sample_rate = 44100
        self.duration = 0.5  # seconds
        self.volume = 0.5
        self.audio_queue = queue.Queue()
        self.playing_thread = None
        self.is_playing = False

    def create_direction_cue(self, direction):
        """Create an audio cue for a specific direction"""
        try:
            # Convert direction to angle (0-360 degrees)
            angle = self._direction_to_angle(direction)
            
            # Generate stereo audio signal
            signal = self._generate_directional_signal(angle)
            
            # Add to queue
            self.audio_queue.put(signal)
            
            # Start playing if not already
            if not self.is_playing:
                self._start_playing()
            
            return True
        except Exception as e:
            print(f"Error creating direction cue: {str(e)}")
            return False

    def generate_obstacle_alert(self, obstacle_info):
        """Generate an audio alert for an obstacle"""
        try:
            # Create alert sound based on obstacle type and distance
            signal = self._generate_obstacle_signal(
                obstacle_info.get('type', 'unknown'),
                obstacle_info.get('distance', 'unknown')
            )
            
            # Add to queue
            self.audio_queue.put(signal)
            
            # Start playing if not already
            if not self.is_playing:
                self._start_playing()
            
            return True
        except Exception as e:
            print(f"Error generating obstacle alert: {str(e)}")
            return False

    def _direction_to_angle(self, direction):
        """Convert direction text to angle in degrees"""
        direction_map = {
            'ahead': 0,
            'right': 90,
            'behind': 180,
            'left': 270,
            'slightly right': 45,
            'slightly left': 315
        }
        return direction_map.get(direction.lower(), 0)

    def _generate_directional_signal(self, angle):
        """Generate a stereo signal with directional cues"""
        try:
            # Generate time array
            t = np.linspace(0, self.duration, int(self.sample_rate * self.duration))
            
            # Generate base tone
            frequency = 440  # Hz
            base_tone = np.sin(2 * np.pi * frequency * t)
            
            # Apply volume envelope
            envelope = np.exp(-5 * t)  # Exponential decay
            base_tone = base_tone * envelope
            
            # Convert angle to stereo balance
            # 0 degrees = center, 90 degrees = right, 270 degrees = left
            balance = np.sin(np.radians(angle))
            
            # Create stereo signal
            left = base_tone * (1 - balance) * self.volume
            right = base_tone * (1 + balance) * self.volume
            
            return np.column_stack((left, right))
        except Exception as e:
            print(f"Error generating directional signal: {str(e)}")
            return None

    def _generate_obstacle_signal(self, obstacle_type, distance):
        """Generate an alert signal based on obstacle type and distance"""
        try:
            # Generate time array
            t = np.linspace(0, self.duration, int(self.sample_rate * self.duration))
            
            # Different frequencies for different obstacle types
            frequency_map = {
                'person': 880,
                'chair': 660,
                'table': 550,
                'door': 440,
                'wall': 330
            }
            
            frequency = frequency_map.get(obstacle_type.lower(), 440)
            
            # Generate tone
            tone = np.sin(2 * np.pi * frequency * t)
            
            # Adjust volume based on distance
            distance_volume = {
                'near': 0.8,
                'medium': 0.5,
                'far': 0.3
            }
            
            volume = distance_volume.get(distance.lower(), 0.5) * self.volume
            
            # Apply volume envelope
            envelope = np.exp(-5 * t)  # Exponential decay
            tone = tone * envelope * volume
            
            # Create stereo signal (centered)
            return np.column_stack((tone, tone))
        except Exception as e:
            print(f"Error generating obstacle signal: {str(e)}")
            return None

    def _start_playing(self):
        """Start the audio playback thread"""
        self.is_playing = True
        self.playing_thread = threading.Thread(target=self._playback_loop)
        self.playing_thread.daemon = True
        self.playing_thread.start()

    def _playback_loop(self):
        """Main loop for audio playback"""
        while self.is_playing:
            try:
                # Get next audio signal from queue
                signal = self.audio_queue.get_nowait()
                
                if signal is not None:
                    # Play the audio
                    sd.play(signal, self.sample_rate)
                    sd.wait()  # Wait until finished
                
            except queue.Empty:
                # No more audio to play
                self.is_playing = False
                break
            except Exception as e:
                print(f"Error in audio playback: {str(e)}")
                break

    def stop(self):
        """Stop audio playback"""
        self.is_playing = False
        if self.playing_thread:
            self.playing_thread.join()
        sd.stop() 