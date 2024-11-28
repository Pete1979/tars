import requests
import subprocess

def speak_response(response):
    try:
        url = "http://192.168.0.135:5002/api/tts"
        payload = {
            "text": response,
            "voice": "en_us_male"  # Change this to the desired voice available in xtts-api-server
        }
        headers = {
            "Content-Type": "application/json"
        }
        response = requests.post(url, json=payload, headers=headers)
        if response.status_code == 200:
            with open("response.mp3", "wb") as f:
                f.write(response.content)
            subprocess.run(['mpg123', '-q', 'response.mp3'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        else:
            print(f"Error: Received status code {response.status_code} from TTS server")
    except Exception as e:
        print(f"Error speaking response: {e}")