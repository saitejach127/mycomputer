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

def load_env(env_path=".env"):
    env_vars = {}
    if os.path.exists(env_path):
        with open(env_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    key, value = line.split('=', 1)
                    env_vars[key] = value
    return env_vars

ENV_VARS = load_env()
SERVER_URL = ENV_VARS.get("SERVER_URL", "http://localhost:5001/transcribe")

class VoiceTranscriber(ThemedTk):
    def __init__(self):
        super().__init__()
        self.set_theme("arc")
        self.title("Wispr Clone")
        self.geometry("800x600")

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # --- Navbar ---
        self.navbar_frame = ttk.Frame(self, width=150, relief=tk.RAISED, borderwidth=1)
        self.navbar_frame.grid(row=0, column=0, sticky="nswe")

        self.home_button = ttk.Button(self.navbar_frame, text="Home", command=self.show_home)
        self.home_button.pack(pady=10, padx=10, fill="x")
        
        self.history_button = ttk.Button(self.navbar_frame, text="History", command=self.show_history)
        self.history_button.pack(pady=10, padx=10, fill="x")

        self.todo_button = ttk.Button(self.navbar_frame, text="Todo", command=self.show_todo)
        self.todo_button.pack(pady=10, padx=10, fill="x")

        # --- Content Frames ---
        self.content_frame = ttk.Frame(self)
        self.content_frame.grid(row=0, column=1, sticky="nswe")
        self.content_frame.grid_rowconfigure(0, weight=1)
        self.content_frame.grid_columnconfigure(0, weight=1)

        self.home_frame = self.create_home_frame()
        self.history_frame = self.create_history_frame()
        self.todo_frame = TodoUI(self.content_frame)

        for frame in (self.home_frame, self.history_frame, self.todo_frame):
            frame.grid(row=0, column=0, sticky="nswe")

        # --- App State ---
        self.recording = False
        self.audio_queue = queue.Queue()
        self.keyboard_controller = keyboard.Controller()
        self.listener = keyboard.Listener(on_press=self.on_press, on_release=self.on_release)
        self.listener.start()

        self.show_home()

    def create_home_frame(self):
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
        self.status_var.set("Press and hold Left Option to start recording...")
        status_label = ttk.Label(self.last_transcriptions_frame, textvariable=self.status_var, wraplength=380)
        status_label.pack(pady=5)

        self.transcription_var = tk.StringVar()
        transcription_label = ttk.Label(self.last_transcriptions_frame, textvariable=self.transcription_var, wraplength=380, foreground="blue")
        transcription_label.pack(pady=5)
        
        return frame

    def create_history_frame(self):
        frame = ttk.Frame(self.content_frame)
        self.history_text_area = tk.Text(frame, wrap="word", state="disabled")
        self.history_text_area.pack(expand=True, fill="both", padx=10, pady=10)
        return frame

    def show_home(self):
        self.update_home_tab()
        self.home_frame.tkraise()

    def show_history(self):
        self.update_history_tab()
        self.history_frame.tkraise()

    def show_todo(self):
        self.todo_frame.tkraise()

    def update_home_tab(self):
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

    def update_history_tab(self):
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

    def on_press(self, key):
        if key == keyboard.Key.alt_l and not self.recording:
            self.recording = True
            self.status_var.set("Recording...")
            self.transcription_var.set("")
            self.audio_queue = queue.Queue()
            self.recording_thread = threading.Thread(target=self.record_audio)
            self.recording_thread.start()

    def on_release(self, key):
        if key == keyboard.Key.alt_l and self.recording:
            self.recording = False
            self.status_var.set("Transcribing...")

    def record_audio(self):
        with sd.InputStream(samplerate=16000, channels=1, callback=self.audio_callback):
            while self.recording:
                sd.sleep(100)
        self.process_audio()

    def audio_callback(self, indata, frames, time, status):
        if status:
            print(status)
        self.audio_queue.put(indata.copy())

    def process_audio(self):
        audio_data = []
        while not self.audio_queue.empty():
            audio_data.append(self.audio_queue.get())
        
        if not audio_data:
            self.status_var.set("No audio recorded. Press and hold Left Option...")
            return

        import numpy as np
        audio_data = np.concatenate(audio_data, axis=0)
        sf.write("temp_audio.wav", audio_data, 16000)
        self.transcribe_audio()

    def transcribe_audio(self):
        try:
            with open("temp_audio.wav", 'rb') as f:
                files = {'audio': f}
                response = requests.post(SERVER_URL, files=files)
                if response.status_code == 200:
                    result = response.json()
                    transcribed_text = result.get('transcription', '')
                    self.transcription_var.set(transcribed_text)
                    if transcribed_text:
                        self.keyboard_controller.type(transcribed_text)
                        db.add_transcription(transcribed_text)
                        self.update_home_tab()
                else:
                    self.status_var.set(f"Error: {response.status_code} - {response.text}")
        except Exception as e:
            self.status_var.set(f"Error: {e}")
        finally:
            self.status_var.set("Press and hold Left Option to start recording...")


if __name__ == "__main__":
    app = VoiceTranscriber()
    app.mainloop()