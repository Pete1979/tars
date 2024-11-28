import os
import sys
import time
import json
import asyncio
import subprocess
import pytesseract
import speech_recognition as sr
from modules.camera import initialize_camera, capture_frame
from modules.discord_bot import DiscordBot
from modules.speech_recognition import listen_for_wake_phrase, listen_for_command
from modules.ollama_interaction import interact_with_olama
from modules.tts import speak_response  # Updated import statement
from modules.ocr import describe_camera_view  # Updated import statement

async def main_loop():
    recognizer = sr.Recognizer()
    cap = initialize_camera("/dev/video0")
    
    conversation_active = False
    timeout_start = time.time()
    conversation_timeout = 300

    listening_for_wake = True
    listening_for_command = False

    # Create an instance of the DiscordBot with necessary details
    discord_bot = DiscordBot(bot_token='YOUR_TOKEN_HERE', channel_id='CHANNEL_ID_HERE', char_greeting="Hello! TARS is online.")

    while True:
        if not conversation_active:
            if listening_for_wake:
                print("Listening for wake phrase...")
                listening_for_wake = False
            if listen_for_wake_phrase(recognizer):
                try:
                    speak_response("Huh!? What do you want?")
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
                    speak_response(response_text)
                except Exception as e:
                    print(f"Error responding to command: {e}")
            if time.time() - timeout_start > conversation_timeout:
                conversation_active = False
                listening_for_wake = True
                print("Conversation timed out. Listening for wake phrase...")
                listening_for_command = False

if __name__ == "__main__":
    asyncio.run(main_loop())
