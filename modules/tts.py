import requests
import subprocess

def speak_response(response_text):
    try:
        # TTS server endpoints
        url = "http://192.168.0.135:8020/tts_to_audio/"
        payload = {
            "text": response_text,  # The text to be converted to speech
            "speaker_wav": "TARS2",  # Specify the speaker
            "language": "en"        # Language parameter
        }
        headers = {
            "accept": "application/json",         # Accept JSON response
            "Content-Type": "application/json"    # Send JSON data
        }
        
        # Make the POST request to the TTS server
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()  # Raise HTTPError for bad responses (4xx and 5xx)
        
        # Save the audio file with the correct extension
        audio_file = "response.wav"
        with open(audio_file, "wb") as f:
            f.write(response.content)
        
        # Play the audio using an appropriate audio player
        subprocess.run(['aplay', audio_file], check=True)
    
    except requests.exceptions.RequestException as e:
        print(f"Error in TTS request: {e}")
    except subprocess.CalledProcessError as e:
        print(f"Error playing audio: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        