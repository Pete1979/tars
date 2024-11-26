import os
import sys
import time
import speech_recognition as sr
import json
from ollama_prod import Client, ChatResponse
from contextlib import contextmanager
import asyncio
from edge_tts import Communicate
import subprocess
import cv2
import pytesseract

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

# Initialize the camera
cap = cv2.VideoCapture("/dev/video0")  # Use correct device path for your camera

if not cap.isOpened():
    print("Error: Could not open video stream.")
    sys.exit()

# Function to listen for the wake phrase
def listen_for_wake_phrase():
    with suppress_alsa_output():  # Suppress ALSA output
        with sr.Microphone() as source:
            try:
                audio = recognizer.listen(source)
                phrase = recognizer.recognize_google(audio)
                print(f"You said: {phrase}")
                return "hey buddy" in phrase.lower()  # Match wake phrase
            except sr.UnknownValueError:
                return False  # No need to print if not understood
            except sr.RequestError:
                print("Error with speech recognition service.")
                return False

# Function to listen for a voice command
def listen_for_command():
    with suppress_alsa_output():  # Suppress ALSA output
        with sr.Microphone() as source:
            try:
                audio = recognizer.listen(source)
                command = recognizer.recognize_google(audio)
                print(f"You said: {command}")
                return command
            except sr.UnknownValueError:
                return None  # No need to print if not understood
            except sr.RequestError:
                return None  # Error with the service; return None without printing

# Function to speak a response using Edge TTS
async def speak_response(response):
    voice = "en-US-GuyNeural"  # TARS-like voice
    rate = "-5%"  # Slightly slower delivery
    pitch = "-2Hz"  # Slightly lower pitch for depth
    communicate = Communicate(text=response, voice=voice, rate=rate, volume="+5%")
    await communicate.save("response.mp3")
    subprocess.run(['mpg123', '-q', 'response.mp3'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def load_character_card(file_path):
    """Load the character card JSON file from the charactercards folder."""
    charactercards_folder = "charactercards"
    card_path = os.path.join(charactercards_folder, file_path)
    if not os.path.exists(card_path):
        return None
    with open(card_path, 'r') as file:
        return json.load(file)

# Function to interact with Ollama
def interact_with_olama(command, character_card_file="TARS_alpha.json"):
    character_card = load_character_card(character_card_file)
    if not character_card:
        return "Error: Character card not found."
    personality = character_card.get("personality", "No personality found.")
    url = "http://192.168.0.135:11434"  # Update with Ollama's API endpoint
    payload = command
    c = Client(host=url)
    r: ChatResponse = c.chat(
        model='llama3.2',
        messages=[
            {'role': 'system', 'content': personality},
            {'role': 'user', 'content': payload}
        ]
    )
    return r['message']['content']

# Function to describe the camera's view
def describe_camera_view():
    print("Capturing frame for OCR...")
    ret, frame = cap.read()
    if not ret:
        return "Failed to capture image."
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    text = pytesseract.image_to_string(gray)
    return f"The camera sees the following text: {text}" if text.strip() else "I could not detect any text."

# Main loop
print("Starting TARS...")
conversation_active = False
timeout_start = time.time()
conversation_timeout = 300  # 5 minutes of inactivity ends conversation

# Flags to track listening state
listening_for_wake = True
listening_for_command = False

while True:
    if not conversation_active:
        if listening_for_wake:  # Print once for wake phrase listening
            print("Listening for wake phrase...")
            listening_for_wake = False  # Prevent further spamming
        if listen_for_wake_phrase():  # Wake phrase detected
            asyncio.run(speak_response("Huh!?"))  # Respond to wake phrase
            conversation_active = True
            timeout_start = time.time()
            listening_for_command = True  # Start listening for commands
            print("Listening for a command...")  # Print command listening once
            listening_for_wake = True  # Ensure we reset the wake flag when the command listening starts
    else:
        if listening_for_command:  # Only print once for command listening
            listening_for_command = False  # Prevent further spamming
        command = listen_for_command()  # Listen for a command
        if command:
            timeout_start = time.time()  # Reset timeout
            if "what do you see" in command.lower():
                response_text = describe_camera_view()
            else:
                response_text = interact_with_olama(command)
            print(f"Response: {response_text}")
            asyncio.run(speak_response(response_text))
        if time.time() - timeout_start > conversation_timeout:
            conversation_active = False  # End conversation after timeout
            listening_for_wake = True  # Go back to listening for wake phrase
            print("Conversation timed out. Listening for wake phrase...")
            listening_for_command = False  # Reset command listening
