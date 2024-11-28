import requests

url = "http://192.168.0.135:8020/tts_to_audio/"
payload = {"text": "Hello, testing TTS server!"}
headers = {"Content-Type": "application/json"}

try:
    response = requests.post(url, json=payload, headers=headers)
    response.raise_for_status()
    print("TTS response received:", response.content)
except requests.exceptions.RequestException as e:
    print("Error:", e)
