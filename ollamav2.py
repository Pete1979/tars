import os
import sys
import speech_recognition as sr
import json
from ollama import Client, ChatResponse
from contextlib import contextmanager
import asyncio
from edge_tts import Communicate
import cv2
import face_recognition
import pytesseract
import mediapipe as mp
import numpy as np
import tensorflow as tf

# Suppression context manager
@contextmanager
def suppress_alsa_output():
    """Redirect stderr to /dev/null to suppress ALSA warnings."""
    devnull = os.open(os.devnull, os.O_WRONLY)
    old_stderr = os.dup(2)
    os.dup2(devnull, 2)
    os.close(devnull)
    try:
        yield
    finally:
        os.dup2(old_stderr, 2)
        os.close(old_stderr)

# Initialize the speech recognizer
recognizer = sr.Recognizer()

# Initialize the camera (using OpenCV)
def capture_face_image():
    """Capture image from camera and detect faces."""
    video_capture = cv2.VideoCapture(0)  # Use the default camera
    if not video_capture.isOpened():
        print("Error: Could not access the camera.")
        return None
    
    # Capture a frame from the camera
    ret, frame = video_capture.read()
    if not ret:
        print("Error: Could not read frame.")
        return None
    
    # Convert image to RGB (OpenCV uses BGR by default)
    rgb_frame = frame[:, :, ::-1]
    
    # Use face_recognition to detect faces
    face_locations = face_recognition.face_locations(rgb_frame)
    
    # Optionally: draw a rectangle around the faces
    for (top, right, bottom, left) in face_locations:
        cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
    
    # Save the captured image (for debugging purposes)
    image_path = "captured_face.jpg"
    cv2.imwrite(image_path, frame)
    
    # Release the camera
    video_capture.release()
    return image_path, face_locations, frame

# Gesture Recognition (using Mediapipe)
def recognize_gesture(frame):
    """Detect hand gestures and trigger TARS commands."""
    mp_hands = mp.solutions.hands
    hands = mp_hands.Hands()
    
    # Process the frame
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(frame_rgb)
    
    if results.multi_hand_landmarks:
        # Here we can recognize gestures by analyzing landmarks
        print("Hand gesture detected!")
        return True
    return False

# Object Recognition (using TensorFlow and MobileNet)
def recognize_objects(frame):
    """Use MobileNet to detect objects in the environment."""
    model = tf.saved_model.load('mobilenet_model_path')  # Use a path to your saved model
    
    input_tensor = tf.convert_to_tensor(frame)
    input_tensor = input_tensor[tf.newaxis,...]  # Add batch dimension
    detections = model(input_tensor)
    
    # Here, you can analyze the detections and extract object info
    print("Object detection output:", detections)
    return detections

# Reading Text (OCR)
def read_text_from_image(frame):
    """Perform OCR on the captured frame."""
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    text = pytesseract.image_to_string(gray)
    print(f"Detected text: {text}")
    return text

# Motion Detection (using OpenCV)
def detect_motion():
    """Detect motion in front of the camera."""
    video_capture = cv2.VideoCapture(0)  # Use the default camera
    ret, frame1 = video_capture.read()
    ret, frame2 = video_capture.read()
    
    while ret:
        # Compute the difference between frames
        diff = cv2.absdiff(frame1, frame2)
        gray = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
        _, thresh = cv2.threshold(gray, 25, 255, cv2.THRESH_BINARY)
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        for contour in contours:
            if cv2.contourArea(contour) > 500:  # Minimum contour size
                print("Motion detected!")
                return True  # Motion detected
        
        frame1 = frame2
        ret, frame2 = video_capture.read()
    
    video_capture.release()
    return False  # No motion detected

# Function to listen for a voice command
def listen_for_command():
    with suppress_alsa_output():  # Suppress ALSA output
        with sr.Microphone() as source:
            print("Listening for a command...")
            audio = recognizer.listen(source)
            try:
                command = recognizer.recognize_google(audio)
                print(f"You said: {command}")
                return command
            except sr.UnknownValueError:
                print("Sorry, I did not understand that.")
                return None
            except sr.RequestError:
                print("Sorry, there was an error with the speech recognition service.")
                return None

# Function to speak a response using Edge TTS
async def speak_response(response):
    voice = "en-US-AriaNeural"  # Choose a realistic neural voice
    communicate = Communicate(text=response, voice=voice, rate="-10%")  # Adjust rate to slow down
    await communicate.save("response.mp3")
    os.system("mpg123 response.mp3")  # Requires mpg123 or a similar MP3 player

def load_character_card(file_path):
    """Load the character card JSON file."""
    with open(file_path, 'r') as file:
        return json.load(file)

# Function to interact with Ollama
def interact_with_olama(command):
    # Load character card
    character_card = load_character_card("TARS_alpha.json")
    personality = character_card["personality"]  # Extract personality details

    # Replace this with actual API query to Ollama
    url = "http://192.168.0.135:11434"  # Update with Ollama's API endpoint
    payload = '%s' % command
    c = Client(
        host=url
    )
    r: ChatResponse = c.chat(
        model='llama3.2',
        messages=[
            {
                'role': 'system',
                'content': personality  # Use personality from the character card
            },
            {
                'role': 'user',
                'content': payload  # Use payload here directly, not as a string
            }
        ]
    )
    r_str = r['message']['content']
    print(r_str)
    return r_str

# Main loop
while True:
    # Capture face and detect face location
    image_path, face_locations, frame = capture_face_image()
    if face_locations:
        print(f"Detected faces: {face_locations}")
    else:
        print("No faces detected.")
    
    # Detect motion
    if detect_motion():
        print("Motion detected. Waking up TARS.")
    
    # Recognize gestures (hand gestures)
    if recognize_gesture(frame):
        print("Gesture recognized!")
    
    # Recognize objects
    recognize_objects(frame)
    
    # OCR (Reading text)
    detected_text = read_text_from_image(frame)
    
    # Listen for a voice command
    command = listen_for_command()
    if command:
        response = interact_with_olama(command)
        asyncio.run(speak_response(response))
