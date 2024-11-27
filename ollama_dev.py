import os
import sys
import time
import speech_recognition as sr
import json
from ollama import Client, ChatResponse
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

def listen_for_wake_phrase():
    """
    Listen for the wake phrase using the microphone.
    
    Returns:
        bool: True if wake phrase is detected, otherwise False.
    """
    with suppress_alsa_output():  # Suppress ALSA output
        with sr.Microphone() as source:
            try:
                audio = recognizer.listen(source)
                phrase = recognizer.recognize_google(audio)
                print(f"You said: {phrase}")
                return "hey buddy" in phrase.lower()  # Match wake phrase
            except sr.UnknownValueError:
                return False  # No need to print if not understood
            except sr.RequestError as e:
                print(f"Error with speech recognition service: {e}")
                return False
            except Exception as e:
                print(f"Unexpected error: {e}")
                return False

def listen_for_command():
    """
    Listen for a voice command using the microphone.
    
    Returns:
        str: The recognized command, or None if not understood or an error occurs.
    """
    with suppress_alsa_output():  # Suppress ALSA output
        with sr.Microphone() as source:
            try:
                audio = recognizer.listen(source)
                command = recognizer.recognize_google(audio)
                print(f"You said: {command}")
                return command
            except sr.UnknownValueError:
                return None  # No need to print if not understood
            except sr.RequestError as e:
                print(f"Error with speech recognition service: {e}")
                return None
            except Exception as e:
                print(f"Unexpected error: {e}")
                return None

async def speak_response(response):
    """
    Speak a response using Edge TTS.
    
    Args:
        response (str): The text response to speak.
    """
    try:
        voice = "en-US-GuyNeural"  # TARS-like voice
        rate = "-5%"  # Slightly slower delivery
        pitch = "-2Hz"  # Slightly lower pitch for depth
        communicate = Communicate(text=response, voice=voice, rate=rate, volume="+5%")
        await communicate.save("response.mp3")
        subprocess.run(['mpg123', '-q', 'response.mp3'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception as e:
        print(f"Error speaking response: {e}")

def load_character_card(file_path):
    """
    Load the character card JSON file from the charactercards folder.
    
    Args:
        file_path (str): The path to the character card file.
    
    Returns:
        dict: The content of the character card file, or None if the file does not exist.
    """
    charactercards_folder = "charactercards"
    card_path = os.path.join(charactercards_folder, file_path)
    if not os.path.exists(card_path):
        print(f"Error: Character card file {file_path} not found.")
        return None
    try:
        with open(card_path, 'r') as file:
            return json.load(file)
    except Exception as e:
        print(f"Error loading character card: {e}")
        return None

def interact_with_olama(command, character_card_file="TARS_alpha.json"):
    """
    Interact with Ollama using a given command and character card.
    
    Args:
        command (str): The command to send to Ollama.
        character_card_file (str): The character card file to use.
    
    Returns:
        str: The response from Ollama.
    """
    character_card = load_character_card(character_card_file)
    if not character_card:
        return "Error: Character card not found."
    personality = character_card.get("personality", "No personality found.")
    url = "http://192.168.0.135:11434"  # Update with Ollama's API endpoint
    payload = command
    try:
        c = Client(host=url)
        r: ChatResponse = c.chat(
            model='llama3.2',
            messages=[
                {'role': 'system', 'content': personality},
                {'role': 'user', 'content': payload}
            ]
        )
        return r['message']['content']
    except Exception as e:
        print(f"Error interacting with Ollama: {e}")
        return "Error interacting with Ollama."

def describe_camera_view():
    """
    Capture an image from the camera and perform OCR to describe the view.
    
    Returns:
        str: The text detected in the camera view, or an error message if detection fails.
    """
    print("Capturing frame for OCR...")
    try:
        ret, frame = cap.read()
        if not ret:
            return "Failed to capture image."
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        text = pytesseract.image_to_string(gray)
        return f"The camera sees the following text: {text}" if text.strip() else "I could not detect any text."
    except Exception as e:
        print(f"Error describing camera view: {e}")
        return "Error describing camera view."

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
            try:
                asyncio.run(speak_response("Huh!? What do you want?"))  # Respond to wake phrase
            except Exception as e:
                print(f"Error responding to wake phrase: {e}")
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
            try:
                asyncio.run(speak_response(response_text))
            except Exception as e:
                print(f"Error responding to command: {e}")
        if time.time() - timeout_start > conversation_timeout:
            conversation_active = False  # End conversation after timeout
            listening_for_wake = True  # Go back to listening for wake phrase
            print("Conversation timed out. Listening for wake phrase...")
            listening_for_command = False  # Reset command listening
