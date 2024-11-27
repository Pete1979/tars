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

@contextmanager
def suppress_alsa_output():
    devnull = os.open(os.devnull, os.O_WRONLY)
    old_stderr = os.dup(2)
    os.dup2(devnull, 2)
    os.close(devnull)
    try:
        yield
    finally:
        os.dup2(old_stderr, 2)
        os.close(old_stderr)

async def speak_response(response):
    try:
        voice = "en-US-GuyNeural"
        rate = "-5%"
        pitch = "-2Hz"
        communicate = Communicate(text=response, voice=voice, rate=rate, volume="+5%")
        await communicate.save("response.mp3")
        subprocess.run(['mpg123', '-q', 'response.mp3'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception as e:
        print(f"Error speaking response: {e}")

def load_character_card(file_path):
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

def interact_with_olama(command, character_card_file="TARS_alpha.json", user_name="human"):
    character_card = load_character_card(character_card_file)
    if not character_card:
        return "Error: Character card not found."
    
    personality = character_card.get("personality", "No personality found.")
    scenario = character_card.get("scenario", "No scenario found.")
    greeting = character_card.get("char_greeting", "No greeting found.")
    example_dialogue = character_card.get("example_dialogue", "No example dialogue found.")
    quirks = character_card.get("metadata", {}).get("quirks", {})
    
    # Replace {{user}} with user_name in all relevant fields
    personality = personality.replace("{{user}}", user_name)
    scenario = scenario.replace("{{user}}", user_name)
    greeting = greeting.replace("{{user}}", user_name)
    example_dialogue = example_dialogue.replace("{{user}}", user_name)
    for key, value in quirks.items():
        if isinstance(value, str):
            quirks[key] = value.replace("{{user}}", user_name)
    
    url = "http://192.168.0.135:11434"
    payload = command
    try:
        c = Client(host=url)
        r: ChatResponse = c.chat(
            model='llama3.2',
            messages=[
                {'role': 'system', 'content': f"{personality}\n{scenario}\n{greeting}\n{example_dialogue}\n{quirks}"},
                {'role': 'user', 'content': payload}
            ]
        )
        return r['message']['content'].replace("{{user}}", user_name)
    except Exception as e:
        print(f"Error interacting with Ollama: {e}")
        return "Error interacting with Ollama."

def describe_camera_view(cap):
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

def listen_for_wake_phrase(recognizer):
    with suppress_alsa_output():
        with sr.Microphone() as source:
            try:
                audio = recognizer.listen(source)
                phrase = recognizer.recognize_google(audio)
                print(f"You said: {phrase}")
                return "hey buddy" in phrase.lower()
            except sr.UnknownValueError:
                return False
            except sr.RequestError as e:
                print(f"Error with speech recognition service: {e}")
                return False
            except Exception as e:
                print(f"Unexpected error: {e}")
                return False

def listen_for_command(recognizer):
    with suppress_alsa_output():
        with sr.Microphone() as source:
            try:
                audio = recognizer.listen(source)
                command = recognizer.recognize_google(audio)
                print(f"You said: {command}")
                return command
            except sr.UnknownValueError:
                return None
            except sr.RequestError as e:
                print(f"Error with speech recognition service: {e}")
                return None
            except Exception as e:
                print(f"Unexpected error: {e}")
                return None

async def main_loop():
    recognizer = sr.Recognizer()
    cap = cv2.VideoCapture("/dev/video0")
    if not cap.isOpened():
        print("Error: Could not open video stream.")
        sys.exit()
    
    conversation_active = False
    timeout_start = time.time()
    conversation_timeout = 300

    listening_for_wake = True
    listening_for_command = False

    while True:
        if not conversation_active:
            if listening_for_wake:
                print("Listening for wake phrase...")
                listening_for_wake = False
            if listen_for_wake_phrase(recognizer):
                try:
                    await speak_response("Huh!? What do you want?")
                except Exception as e:
                    print(f"Error responding to wake phrase: {e}")
                conversation_active = True
                timeout_start = time.time()
                listening_for_command = True
                print("Listening for a command...")
                listening_for_wake = True
        else:
            if listening_for_command:
                listening_for_command = False
            command = listen_for_command(recognizer)
            if command:
                timeout_start = time.time()
                if "what do you see" in command.lower():
                    response_text = describe_camera_view(cap)
                else:
                    response_text = interact_with_olama(command)
                print(f"Response: {response_text}")
                try:
                    await speak_response(response_text)
                except Exception as e:
                    print(f"Error responding to command: {e}")
            if time.time() - timeout_start > conversation_timeout:
                conversation_active = False
                listening_for_wake = True
                print("Conversation timed out. Listening for wake phrase...")
                listening_for_command = False

if __name__ == "__main__":
    asyncio.run(main_loop())
