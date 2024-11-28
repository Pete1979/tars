import requests
import subprocess

def speak_response(response):
    try:
        url = "http://192.168.0.135:8020/api/tts"  # Updated port to 8020
        payload = {
            "text": response,
            "voice": "en_us_male"  # Change this to the desired voice available in xtts-api-server
        }
        headers = {
            "Content-Type": "application/json"
        }
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()  # Raise an HTTPError for bad responses (4xx and 5xx)
        with open("response.mp3", "wb") as f:
            f.write(response.content)
        subprocess.run(['mpg123', '-q', 'response.mp3'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except requests.exceptions.RequestException as e:
        print(f"Error speaking response: {e}")