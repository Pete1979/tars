import requests
import subprocess
import threading
import queue
import tempfile

def stream_audio(audio_queue):
    process = subprocess.Popen(['ffplay', '-i', 'pipe:0', '-autoexit', '-nodisp'], stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    while True:
        chunk = audio_queue.get()
        if chunk is None:
            break
        process.stdin.write(chunk)

    process.stdin.close()
    process.wait()

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
        response = requests.post(url, json=payload, headers=headers, stream=True)
        response.raise_for_status()  # Raise HTTPError for bad responses (4xx and 5xx)

        # Create a queue to buffer audio chunks
        audio_queue = queue.Queue()
        thread = threading.Thread(target=stream_audio, args=(audio_queue,))
        thread.start()

        # Put chunks in the queue
        for chunk in response.iter_content(chunk_size=4096):  # Increased chunk size
            audio_queue.put(chunk)

        # Signal the end of streaming
        audio_queue.put(None)
        thread.join()

    except requests.exceptions.RequestException as e:
        print(f"Error in TTS request: {e}")
    except subprocess.CalledProcessError as e:
        print(f"Error playing audio: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

# Example of how to call the speak_response function
speak_response("Hello, this is a test response.")
