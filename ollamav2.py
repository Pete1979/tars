import os
import sys
import speech_recognition as sr
import json
from ollama import Client, ChatResponse
from contextlib import contextmanager
import asyncio
from edge_tts import Communicate
import subprocess

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
        print(f"[DEBUG] Character card file '{file_path}' not found in '{charactercards_folder}' directory.")
        return None

    print(f"[DEBUG] Loading character card from: {card_path}")
    with open(card_path, 'r') as file:
        character_card = json.load(file)
        print(f"[DEBUG] Loaded character card: {json.dumps(character_card, indent=2)}")
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
    print(f"[DEBUG] Response from Ollama: {r_str}")
    return r_str

# Main loop
print("Listening for a command...")  # Print once when starting the loop

while True:
    command = listen_for_command()
    if command:
        response = interact_with_olama(command)
        asyncio.run(speak_response(response))
        print("Listening for a command...")  # Print again after each response
