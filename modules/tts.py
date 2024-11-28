import subprocess
from edge_tts import Communicate

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