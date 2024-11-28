import os
import speech_recognition as sr
from contextlib import contextmanager

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