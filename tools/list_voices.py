import pyttsx3

# Initialize the TTS engine
engine = pyttsx3.init()

# List available voices
voices = engine.getProperty('voices')
print("Available voices:")
for index, voice in enumerate(voices):
    print(f"Voice {index}:")
    print(f"  - ID: {voice.id}")
    print(f"  - Name: {voice.name}")
    print(f"  - Languages: {voice.languages}")
    print(f"  - Gender: {voice.gender}")
    print(f"  - Age: {voice.age}")

