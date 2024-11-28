# TARS

TARS is a project designed for advanced speech recognition, text-to-speech, and interaction with external APIs such as Ollama and Discord Bots.

## Features

- **Speech Recognition**: Utilizes Google's speech recognition to listen for wake phrases and commands.
- **Text-to-Speech (TTS)**: Converts text to speech using Edge TTS and custom TTS server.
- **Camera Interaction**: Captures and processes video frames to detect motion and perform OCR.
- **Discord Bot Integration**: Interacts with users via a Discord bot.

## Prerequisites

- Python 3.x
- `pip` (Python package installer)
- Necessary Python packages (listed in `requirements.txt`)

## Installation

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/Pete1979/tars.git
   cd tars
Install Dependencies:
pip install -r requirements.txt
Usage
Speech Recognition and TTS
Run the ollama_prod.py script:

python ollama_prod.py
Listen for Wake Phrase:
The script will listen for the wake phrase "hey buddy" and then process subsequent voice commands.

Interact with Ollama:
Customize the interact_with_olama function to interact with the Ollama API using specific character cards.

Discord Bot
Set Up Discord Bot:

Create a new bot on the Discord Developer Portal.
Copy the bot token and add it to your environment variables.
Run the Discord Bot:

python modules/discord_bot.py
Interact with the Bot:
Mention the bot in any channel it has access to and it will process your messages.

Motion Detection
Run the Motion Detection Test:

python tests/motiondetecttest.py
Monitor Motion:
The script will detect motion and save frames where motion is detected.

Configuration
TTS Server Configuration:
Edit the TTS server endpoint in modules/tts.py to point to your TTS server.

Camera Device Path:
Update the camera device path in ollama_prod.py and tests/motiondetecttest.py to match your system's configuration.

Contributing
Fork the repository.
Create a new branch (git checkout -b feature-branch).
Make your changes.
Commit your changes (git commit -am 'Add new feature').
Push to the branch (git push origin feature-branch).
Create a new Pull Request.
License
This project is licensed under the MIT License. See the LICENSE file for details.

Acknowledgments
Inspired by the TARS robot from the movie "Interstellar".
Uses various open-source libraries and APIs for functionality.