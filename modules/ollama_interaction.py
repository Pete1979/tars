import os
import json
from ollama import Client, ChatResponse

def load_character_card(file_path):
    charactercards_folder = "charactercards"
    card_path = os.path.join(charactercards_folder, file_path)
    if not os.path.exists(card_path):
        print(f"Error: Character card file {file_path} not found.")
        return None
    try:
        with open(card_path, 'r') as file:
            return json.load(file)
    except Exception as e:
        print(f"Error loading character card: {e}")
        return None

def interact_with_olama(command, character_card_file="TARS_alpha.json", user_name="human"):
    character_card = load_character_card(character_card_file)
    if not character_card:
        return "Error: Character card not found."
    
    personality = character_card.get("personality", "No personality found.")
    scenario = character_card.get("scenario", "No scenario found.")
    greeting = character_card.get("char_greeting", "No greeting found.")
    example_dialogue = character_card.get("example_dialogue", "No example dialogue found.")
    quirks = character_card.get("metadata", {}).get("quirks", {})
    
    # Replace {{user}} with user_name in all relevant fields
    personality = personality.replace("{{user}}", user_name)
    scenario = scenario.replace("{{user}}", user_name)
    greeting = greeting.replace("{{user}}", user_name)
    example_dialogue = example_dialogue.replace("{{user}}", user_name)
    for key, value in quirks.items():
        if isinstance(value, str):
            quirks[key] = value.replace("{{user}}", user_name)
    
    url = "http://192.168.0.135:11434"
    payload = command
    try:
        c = Client(host=url)
        r: ChatResponse = c.chat(
            model='llama3.2',
            messages=[
                {'role': 'system', 'content': f"{personality}\n{scenario}\n{greeting}\n{example_dialogue}\n{quirks}"},
                {'role': 'user', 'content': payload}
            ]
        )
        return r['message']['content'].replace("{{user}}", user_name)
    except Exception as e:
        print(f"Error interacting with Ollama: {e}")
        return "Error interacting with Ollama."