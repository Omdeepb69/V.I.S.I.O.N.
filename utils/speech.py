import speech_recognition as sr
import pyttsx3
import threading
import queue
from transformers import pipeline
import pytesseract
import cv2
import numpy as np

class SpeechProcessor:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.engine = pyttsx3.init()
        self.command_queue = queue.Queue()
        self.is_listening = False
        self.listening_thread = None
        self.nlp = pipeline("question-answering")
        self.ocr = pytesseract

    def initialize(self):
        """Initialize speech recognition and text-to-speech"""
        try:
            # Configure text-to-speech engine
            self.engine.setProperty('rate', 150)  # Speed of speech
            self.engine.setProperty('volume', 0.9)  # Volume (0.0 to 1.0)
            
            # Test microphone
            with sr.Microphone() as source:
                self.recognizer.adjust_for_ambient_noise(source)
            
            print("Speech processor initialized successfully")
            return True
        except Exception as e:
            print(f"Failed to initialize speech processor: {str(e)}")
            return False

    def process_natural_language(self, text, context):
        """Process natural language queries using transformers"""
        try:
            result = self.nlp(question=text, context=context)
            return result['answer']
        except Exception as e:
            print(f"Error in NLP processing: {str(e)}")
            return None

    def read_text_in_image(self, frame):
        """Perform OCR on the frame to read text"""
        try:
            # Convert to grayscale
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # Apply thresholding
            _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            
            # Perform OCR
            text = self.ocr.image_to_string(binary)
            return text.strip()
        except Exception as e:
            print(f"Error in text reading: {str(e)}")
            return ""

    def detect_persons(self, frame):
        """Detect persons in the frame"""
        try:
            # Convert to grayscale
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # Load pre-trained face detector
            face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
            
            # Detect faces
            faces = face_cascade.detectMultiScale(gray, 1.3, 5)
            
            return len(faces)
        except Exception as e:
            print(f"Error in person detection: {str(e)}")
            return 0

    def speak(self, text):
        """Convert text to speech"""
        try:
            self.engine.say(text)
            self.engine.runAndWait()
            return True
        except Exception as e:
            print(f"Error in text-to-speech: {str(e)}")
            return False

    def listen(self):
        """Listen for and process voice commands"""
        try:
            with sr.Microphone() as source:
                print("Listening...")
                audio = self.recognizer.listen(source)
                
                try:
                    text = self.recognizer.recognize_google(audio)
                    print(f"Recognized: {text}")
                    return text
                except sr.UnknownValueError:
                    print("Could not understand audio")
                    return None
                except sr.RequestError as e:
                    print(f"Could not request results; {e}")
                    return None
        except Exception as e:
            print(f"Error in speech recognition: {str(e)}")
            return None

    def start_listening(self, callback):
        """Start continuous listening for voice commands"""
        if self.is_listening:
            return False
        
        self.is_listening = True
        self.listening_thread = threading.Thread(
            target=self._listening_loop,
            args=(callback,)
        )
        self.listening_thread.daemon = True
        self.listening_thread.start()
        return True

    def stop_listening(self):
        """Stop continuous listening"""
        self.is_listening = False
        if self.listening_thread:
            self.listening_thread.join()
        return True

    def _listening_loop(self, callback):
        """Main loop for continuous listening"""
        while self.is_listening:
            command = self.listen()
            if command:
                self.command_queue.put(command)
                if callback:
                    callback(command)

    def get_next_command(self):
        """Get the next command from the queue"""
        try:
            return self.command_queue.get_nowait()
        except queue.Empty:
            return None

    def cleanup(self):
        """Clean up resources"""
        self.stop_listening()
        self.engine.stop() 