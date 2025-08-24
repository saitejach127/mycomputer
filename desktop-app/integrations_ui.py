import tkinter as tk
from tkinter import ttk
import webbrowser

class IntegrationsUI(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)

        self.main_frame = ttk.Frame(self)
        self.main_frame.pack(expand=True, fill="both", padx=10, pady=10)

        connect_button = ttk.Button(self.main_frame, text="Connect with Google", command=self.connect_google)
        connect_button.pack(pady=20)

    def connect_google(self):
        """Opens the user's web browser to the auth server's authorize URL."""
        auth_server_url = "http://localhost:5003/authorize"
        webbrowser.open(auth_server_url)