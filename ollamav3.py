import os
import sys
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

# Create a directory to store captured and processed images for later inspection
output_dir = "captured_images"
os.makedirs(output_dir, exist_ok=True)

# Function to listen for a voice command
def listen_for_command():
    with suppress_alsa_output():  # Suppress ALSA output
        with sr.Microphone() as source:
            audio = recognizer.listen(source)
            try:
                command = recognizer.recognize_google(audio)
                print(f"You said: {command}")
                return command
            except sr.UnknownValueError:
                return None  # No need to print or say anything if command is not understood
            except sr.RequestError:
                print("Sorry, there was an error with the speech recognition service.")
                return None

# Function to speak a response using Edge TTS
async def speak_response(response):
    voice = "en-US-GuyNeural"  # TARS-like voice
    rate = "-5%"  # Slightly slower delivery
    pitch = "-2Hz"  # Slightly lower pitch for depth
    communicate = Communicate(text=response, voice=voice, rate=rate, volume="+5%")
    
    # Save the audio response to a file
    await communicate.save("response.mp3")
    
    # Use subprocess to suppress mpg123 output
    subprocess.run(['mpg123', '-q', 'response.mp3'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def load_character_card(file_path):
    """Load the character card JSON file from the charactercards folder."""
    charactercards_folder = "charactercards"
    card_path = os.path.join(charactercards_folder, file_path)
    
    if not os.path.exists(card_path):
        return None

    with open(card_path, 'r') as file:
        character_card = json.load(file)
        return character_card

# Function to interact with Ollama
def interact_with_olama(command, character_card_file="TARS_alpha.json"):
    # Load character card from the charactercards folder
    character_card = load_character_card(character_card_file)
    
    if character_card is None:
        return "Error: Character card not found."

    personality = character_card.get("personality", "No personality found.")  # Extract personality details

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
    return r_str

# Function to detect and read text from the camera with preprocessing
def detect_and_read_text():
    print("Capturing frame for OCR...")
    
    # Capture the frame from the camera
    ret, frame = cap.read()
    
    if not ret:
        print("Failed to capture image.")
        return "Failed to capture image."

    print("Image captured. Processing for OCR...")

    # Convert the frame to grayscale for better OCR accuracy
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Apply thresholding to improve contrast (binary image)
    _, thresholded = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)

    # Optionally apply some blurring or denoising to remove noise
    denoised = cv2.fastNlMeansDenoising(thresholded, None, 30, 7, 21)

    # Resize image to enhance text size (optional)
    resized = cv2.resize(denoised, None, fx=1.5, fy=1.5, interpolation=cv2.INTER_LINEAR)

    # Save the processed image for later inspection
    processed_image_path = os.path.join(output_dir, "processed_image.png")
    cv2.imwrite(processed_image_path, resized)  # Save processed image to file

    # Use pytesseract to extract text from the processed image
    text = pytesseract.image_to_string(resized)

    print(f"OCR Result: {text}")  # Debugging print

    if text.strip():  # Only speak if there's recognizable text
        print(f"Recognized text: {text}")
        return f"I see the following text: {text}"
    else:
        print("No text detected.")
        return "I could not detect any text."

# Main loop
print("Listening for a command...")  # Print once when starting the loop

while True:
    command = listen_for_command()
    if command:
        print(f"Command received: {command}")
        if "what do you see" in command.lower():
            response_text = detect_and_read_text()
        else:
            response_text = interact_with_olama(command)

        print(f"Response after OCR: {response_text}")  # Print the response
        asyncio.run(speak_response(response_text))  # Speak the response
        print("Listening for a command...")  # Print again after each response
