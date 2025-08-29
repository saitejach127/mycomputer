import tkinter as tk
from tkinter import ttk
import sounddevice as sd
import soundfile as sf
import requests
import threading
from pynput import keyboard
import queue
import os
from datetime import datetime, timedelta

from ttkthemes import ThemedTk

import db
from todo_ui import TodoUI
from gemini_ui import GeminiUI
from integrations_ui import IntegrationsUI
from gemini import get_gemini_response as get_gemini_response_from_api

def load_env(env_path=".env"):
    print("Loading environment variables...")
    env_vars = {}
    if os.path.exists(env_path):
        with open(env_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    key, value = line.split('=', 1)
                    env_vars[key] = value
    print("Environment variables loaded.")
    return env_vars

ENV_VARS = load_env()
SERVER_URL = ENV_VARS.get("SERVER_URL", "http://localhost:5001/transcribe")
GEMINI_API_KEY = ENV_VARS.get("GEMINI_API_KEY")

class VoiceTranscriber(ThemedTk):
    def __init__(self):
        super().__init__()
        print("Initializing VoiceTranscriber application...")
        self.set_theme("arc")
        self.title("Wispr Clone")
        self.geometry("800x600")

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # --- Gemini UI ---
        print("Initializing Gemini UI...")
        self.gemini_ui = GeminiUI(self)

        # --- Navbar ---
        print("Creating Navbar...")
        self.navbar_frame = ttk.Frame(self, width=150, relief=tk.RAISED, borderwidth=1)
        self.navbar_frame.grid(row=0, column=0, sticky="nswe")

        self.home_button = ttk.Button(self.navbar_frame, text="Home", command=self.show_home)
        self.home_button.pack(pady=10, padx=10, fill="x")
        
        self.history_button = ttk.Button(self.navbar_frame, text="History", command=self.show_history)
        self.history_button.pack(pady=10, padx=10, fill="x")

        self.todo_button = ttk.Button(self.navbar_frame, text="Todo", command=self.show_todo)
        self.todo_button.pack(pady=10, padx=10, fill="x")

        self.integrations_button = ttk.Button(self.navbar_frame, text="Integrations", command=self.show_integrations)
        self.integrations_button.pack(pady=10, padx=10, fill="x")

        # --- Content Frames ---
        print("Creating Content Frames...")
        self.content_frame = ttk.Frame(self)
        self.content_frame.grid(row=0, column=1, sticky="nswe")
        self.content_frame.grid_rowconfigure(0, weight=1)
        self.content_frame.grid_columnconfigure(0, weight=1)

        self.home_frame = self.create_home_frame()
        self.history_frame = self.create_history_frame()
        self.todo_frame = TodoUI(self.content_frame)
        self.integrations_frame = IntegrationsUI(self.content_frame)

        for frame in (self.home_frame, self.history_frame, self.todo_frame, self.integrations_frame):
            frame.grid(row=0, column=0, sticky="nswe")

        # --- App State ---
        print("Initializing App State...")
        self.recording = False
        self.gemini_recording = False
        self.audio_queue = queue.Queue()
        self.keyboard_controller = keyboard.Controller()
        print("Starting keyboard listener...")
        self.listener = keyboard.Listener(on_press=self.on_press, on_release=self.on_release)
        self.listener.start()

        self.show_home()
        print("Application initialized.")

    def create_home_frame(self):
        print("Creating Home Frame...")
        frame = ttk.Frame(self.content_frame)
        frame.grid_rowconfigure(1, weight=1)
        frame.grid_columnconfigure(0, weight=1)
        
        home_title = ttk.Label(frame, text="MyComputer", font=("Arial", 24))
        home_title.grid(row=0, column=0, pady=20, sticky="n")

        self.total_words_label = ttk.Label(frame, text="Total Words: 0", font=("Arial", 12))
        self.total_words_label.grid(row=0, column=0, padx=10, pady=10, sticky="ne")

        self.last_transcriptions_frame = ttk.LabelFrame(frame, text="Last Transcriptions")
        self.last_transcriptions_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nswe")
        
        self.status_var = tk.StringVar()
        self.status_var.set("Press and hold Left Option to type | Right Option for AI")
        status_label = ttk.Label(self.last_transcriptions_frame, textvariable=self.status_var, wraplength=380)
        status_label.pack(pady=5)

        self.transcription_var = tk.StringVar()
        transcription_label = ttk.Label(self.last_transcriptions_frame, textvariable=self.transcription_var, wraplength=380, foreground="blue")
        transcription_label.pack(pady=5)
        
        return frame

    def create_history_frame(self):
        print("Creating History Frame...")
        frame = ttk.Frame(self.content_frame)
        self.history_text_area = tk.Text(frame, wrap="word", state="disabled")
        self.history_text_area.pack(expand=True, fill="both", padx=10, pady=10)
        return frame

    def show_home(self):
        print("Showing Home Frame...")
        self.update_home_tab()
        self.home_frame.tkraise()

    def show_history(self):
        print("Showing History Frame...")
        self.update_history_tab()
        self.history_frame.tkraise()

    def show_todo(self):
        print("Showing Todo Frame...")
        self.todo_frame.tkraise()

    def show_integrations(self):
        print("Showing Integrations Frame...")
        self.integrations_frame.tkraise()

    def update_home_tab(self):
        print("Updating Home Tab...")
        total_words = db.get_total_word_count()
        self.total_words_label.config(text=f"Total Words: {total_words}")
        
        for widget in self.last_transcriptions_frame.winfo_children():
            if isinstance(widget, ttk.Label) and widget.cget("textvariable") not in [str(self.status_var), str(self.transcription_var)]:
                 widget.destroy()

        transcriptions = db.get_transcriptions()
        last_5 = transcriptions[-5:][::-1]
        for entry in last_5:
            text = entry["text"]
            timestamp = datetime.fromisoformat(entry["timestamp"]).strftime("%Y-%m-%d %H:%M:%S")
            word_count = entry["word_count"]
            
            ttk.Label(self.last_transcriptions_frame, text=f"[{timestamp}] ({word_count} words): {text}", wraplength=700, anchor="w", justify="left").pack(padx=5, pady=2, fill="x")
        print("Home Tab updated.")

    def update_history_tab(self):
        print("Updating History Tab...")
        self.history_text_area.config(state="normal")
        self.history_text_area.delete(1.0, tk.END)

        transcriptions = sorted(db.get_transcriptions(), key=lambda x: x["timestamp"], reverse=True)
        
        today = datetime.now().date()
        yesterday = today - timedelta(days=1)
        day_before = today - timedelta(days=2)

        grouped = {"Today": [], "Yesterday": [], "Day Before Yesterday": [], "Older": []}

        for entry in transcriptions:
            entry_date = datetime.fromisoformat(entry["timestamp"]).date()
            if entry_date == today:
                grouped["Today"].append(entry)
            elif entry_date == yesterday:
                grouped["Yesterday"].append(entry)
            elif entry_date == day_before:
                grouped["Day Before Yesterday"].append(entry)
            else:
                grouped["Older"].append(entry)
        
        for group_name, entries in grouped.items():
            if entries:
                self.history_text_area.insert(tk.END, f"\n--- {group_name} ---\n", "header")
                for entry in entries:
                    timestamp = datetime.fromisoformat(entry["timestamp"]).strftime("%Y-%m-%d %H:%M:%S")
                    self.history_text_area.insert(tk.END, f"[{timestamp}] {entry['text']}\n")
        
        self.history_text_area.config(state="disabled")
        self.history_text_area.tag_configure("header", font=("Arial", 12, "bold"))
        print("History Tab updated.")

    def on_press(self, key):
        if key == keyboard.Key.alt_l and not self.recording:
            print("Left Alt pressed. Starting recording for typing...")
            self.recording = True
            self.status_var.set("Recording for typing...")
            self.transcription_var.set("")
            self.audio_queue = queue.Queue()
            self.recording_thread = threading.Thread(target=self.record_audio, args=(False,))
            self.recording_thread.start()
        elif key == keyboard.Key.alt_r and not self.gemini_recording:
            print("Right Alt pressed. Starting recording for Gemini...")
            self.gemini_recording = True
            self.status_var.set("Recording for Gemini...")
            self.transcription_var.set("")
            self.audio_queue = queue.Queue()
            self.recording_thread = threading.Thread(target=self.record_audio, args=(True,))
            self.recording_thread.start()

    def on_release(self, key):
        if key == keyboard.Key.alt_l and self.recording:
            print("Left Alt released. Stopping recording for typing...")
            self.recording = False
            self.status_var.set("Transcribing for typing...")
        elif key == keyboard.Key.alt_r and self.gemini_recording:
            print("Right Alt released. Stopping recording for Gemini...")
            self.gemini_recording = False
            self.status_var.set("Transcribing for Gemini...")

    def record_audio(self, is_gemini):
        print(f"Recording audio for {'Gemini' if is_gemini else 'typing'}...")
        with sd.InputStream(samplerate=16000, channels=1, callback=self.audio_callback):
            if is_gemini:
                while self.gemini_recording:
                    sd.sleep(100)
            else:
                while self.recording:
                    sd.sleep(100)
        print("Recording stopped. Processing audio...")
        self.process_audio(is_gemini)

    def audio_callback(self, indata, frames, time, status):
        if status:
            print(f"Audio callback status: {status}")
        self.audio_queue.put(indata.copy())

    def process_audio(self, is_gemini):
        print("Processing audio data...")
        audio_data = []
        while not self.audio_queue.empty():
            audio_data.append(self.audio_queue.get())
        
        if not audio_data:
            print("No audio data recorded.")
            self.status_var.set("No audio recorded. Press and hold an Option key...")
            return

        import numpy as np
        audio_data = np.concatenate(audio_data, axis=0)
        sf.write("temp_audio.wav", audio_data, 16000)
        print("Audio saved to temp_audio.wav. Transcribing...")
        self.transcribe_audio(is_gemini)

    def transcribe_audio(self, is_gemini):
        print(f"Transcribing audio for {'Gemini' if is_gemini else 'typing'}...")
        try:
            with open("temp_audio.wav", 'rb') as f:
                files = {'audio': f}
                response = requests.post(SERVER_URL, files=files)
                print(f"Transcription server response: {response.status_code}")
                if response.status_code == 200:
                    result = response.json()
                    transcribed_text = result.get('transcription', '')
                    print(f"Transcription result: {transcribed_text}")
                    self.transcription_var.set(transcribed_text)
                    if transcribed_text:
                        if is_gemini:
                            self.gemini_ui.show_question(transcribed_text)
                            print("Sending transcription to Gemini...")
                            gemini_response = get_gemini_response_from_api(transcribed_text, GEMINI_API_KEY)
                            self.gemini_ui.show_response(gemini_response)
                        else:
                            print("Typing out transcription...")
                            self.keyboard_controller.type(transcribed_text)
                            db.add_transcription(transcribed_text)
                            self.update_home_tab()
                else:
                    print(f"Transcription error: {response.text}")
                    self.status_var.set(f"Error: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"An exception occurred during transcription: {e}")
            self.status_var.set(f"Error: {e}")
        finally:
            self.status_var.set("Press and hold Left Option to type | Right Option for AI")


if __name__ == "__main__":
    print("Starting application...")
    app = VoiceTranscriber()
    app.mainloop()
    print("Application closed.")
