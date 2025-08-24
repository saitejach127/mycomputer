import tkinter as tk
from tkinter import ttk, messagebox
import webbrowser
import os
import json
import pickle
import logging
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request

# --- Logging Setup ---
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)

CREDENTIALS_DIR = "google_credentials"
USER_MAPPING_FILE = os.path.join(CREDENTIALS_DIR, "user_mapping.json")

class IntegrationsUI(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)

        if not os.path.exists(CREDENTIALS_DIR):
            os.makedirs(CREDENTIALS_DIR)

        self.main_frame = ttk.Frame(self)
        self.main_frame.pack(expand=True, fill="both", padx=10, pady=10)

        # --- Connection ---
        connect_frame = ttk.LabelFrame(self.main_frame, text="Step 1: Connect")
        connect_frame.pack(fill="x", pady=10)
        connect_button = ttk.Button(connect_frame, text="Connect with Google", command=self.connect_google)
        connect_button.pack(pady=10, padx=10)

        # --- Paste Credentials ---
        paste_frame = ttk.LabelFrame(self.main_frame, text="Step 2: Save Credentials")
        paste_frame.pack(fill="x", pady=10)

        ttk.Label(paste_frame, text="Paste the credentials from your browser here:").pack(pady=5, padx=10, anchor="w")
        self.creds_text = tk.Text(paste_frame, height=8, width=60)
        self.creds_text.pack(pady=5, padx=10, fill="x", expand=True)

        save_button = ttk.Button(paste_frame, text="Save Credentials", command=self.save_credentials)
        save_button.pack(pady=10, padx=10)

    def connect_google(self):
        """Opens the user's web browser to the auth server's authorize URL."""
        auth_server_url = "http://localhost:5003/authorize"
        webbrowser.open(auth_server_url)

    def save_credentials(self):
        logging.info("--- Starting save_credentials ---")
        try:
            creds_json_string = self.creds_text.get("1.0", tk.END).strip()
            logging.info(f"Got credentials string from text box. Length: {len(creds_json_string)}")
            if not creds_json_string:
                logging.error("Credentials string is empty.")
                messagebox.showerror("Error", "Please paste the credentials text from the browser.")
                return

            logging.info("Attempting to load JSON string into dict...")
            creds_info = json.loads(creds_json_string)
            logging.info("Successfully loaded JSON string.")

            logging.info("Attempting to create temporary credentials object...")
            temp_credentials = Credentials.from_authorized_user_info(creds_info)
            logging.info("Successfully created temporary credentials object.")

            logging.info("Attempting to verify token and get email...")
            import google.oauth2.id_token
            id_info = google.oauth2.id_token.verify_oauth2_token(
                creds_info['id_token'], Request(), temp_credentials.client_id
            )
            email = id_info.get('email')
            logging.info(f"Successfully got email: {email}")

            if not email:
                logging.error("Could not determine email from credentials.")
                messagebox.showerror("Error", "Could not determine email from credentials.")
                return

            safe_filename = "".join(c for c in email if c.isalnum() or c in "._-") + ".json"
            token_file = os.path.join(CREDENTIALS_DIR, safe_filename)
            logging.info(f"Generated token file path: {token_file}")

            logging.info("Attempting to save credentials to JSON file...")
            with open(token_file, "w") as f:
                f.write(creds_json_string)
            logging.info("Successfully saved credentials file.")

            logging.info("Attempting to update user mapping...")
            self.update_user_mapping(email, safe_filename)
            logging.info("Successfully updated user mapping.")

            messagebox.showinfo("Success", f"Credentials for {email} have been saved successfully!")
            self.creds_text.delete("1.0", tk.END)
            logging.info("--- Finished save_credentials successfully ---")

        except Exception as e:
            logging.error("An exception occurred in save_credentials:", exc_info=True)
            messagebox.showerror("Error", f"Failed to save credentials. Please ensure you copied the correct text.\n\nDetails: {e}")

    def update_user_mapping(self, email, json_filename):
        mapping = {}
        if os.path.exists(USER_MAPPING_FILE):
            with open(USER_MAPPING_FILE, "r") as f:
                try:
                    mapping = json.load(f)
                except json.JSONDecodeError:
                    pass # File is empty or corrupt

        mapping[email] = json_filename
        
        with open(USER_MAPPING_FILE, "w") as f:
            json.dump(mapping, f, indent=4)