import json
import os
from datetime import datetime

DATA_FILE = "transcription_data.json"
TODO_FILE = "todo_data.json"

def load_data(file_path):
    if os.path.exists(file_path):
        with open(file_path, 'r') as f:
            return json.load(f)
    return {}

def save_data(data, file_path):
    with open(file_path, 'w') as f:
        json.dump(data, f, indent=4)

# --- Transcription Data Functions ---

def get_transcriptions():
    data = load_data(DATA_FILE)
    return data.get("transcriptions", [])

def get_total_word_count():
    data = load_data(DATA_FILE)
    return data.get("total_word_count", 0)

def add_transcription(text):
    data = load_data(DATA_FILE)
    if "transcriptions" not in data:
        data["transcriptions"] = []
    if "total_word_count" not in data:
        data["total_word_count"] = 0

    word_count = len(text.split())
    timestamp = datetime.now().isoformat()
    
    data["transcriptions"].append({
        "text": text,
        "timestamp": timestamp,
        "word_count": word_count
    })
    data["total_word_count"] += word_count
    
    save_data(data, DATA_FILE)

# --- Todo Data Functions ---

def get_todo_lists():
    return load_data(TODO_FILE)

def save_todo_lists(todo_data):
    save_data(todo_data, TODO_FILE)
