import pyttsx3

# Initialize the TTS engine
engine = pyttsx3.init()

# List available voices
voices = engine.getProperty('voices')

# Sample each voice
for index, voice in enumerate(voices):
    print(f"Sampling Voice {index}: {voice.name}")
    engine.setProperty('voice', voice.id)
    engine.say("Hello, I am a sample voice. How do I sound?")
    engine.runAndWait()

