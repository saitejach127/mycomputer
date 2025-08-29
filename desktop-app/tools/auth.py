import os
import json
from google.oauth2.credentials import Credentials

CREDENTIALS_DIR = "google_credentials"
USER_MAPPING_FILE = os.path.join(CREDENTIALS_DIR, "user_mapping.json")

def load_credentials(email):
    """Loads and returns the credentials for a given email."""
    if not os.path.exists(USER_MAPPING_FILE):
        print(f"Error: User mapping file not found at {USER_MAPPING_FILE}")
        return None

    with open(USER_MAPPING_FILE, "r") as f:
        mapping = json.load(f)
    
    json_filename = mapping.get(email)
    if not json_filename:
        print(f"Error: No credentials found for email {email}")
        return None

    token_file_path = os.path.join(CREDENTIALS_DIR, json_filename)
    if not os.path.exists(token_file_path):
        print(f"Error: Token file not found at {token_file_path}")
        return None

    with open(token_file_path, "r") as f:
        creds_info = json.load(f)
    
    credentials = Credentials.from_authorized_user_info(creds_info)
    return credentials
