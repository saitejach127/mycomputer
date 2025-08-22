import tkinter as tk
import sounddevice as sd
import soundfile as sf
import requests
import threading
from pynput import keyboard
import queue
import os

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

class VoiceTranscriber(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Wispr Clone")
        self.geometry("400x200")

        self.status_var = tk.StringVar()
        self.status_var.set("Press and hold Left Option to start recording...")
        self.status_label = tk.Label(self, textvariable=self.status_var, wraplength=380)
        self.status_label.pack(pady=20)

        self.transcription_var = tk.StringVar()
        self.transcription_label = tk.Label(self, textvariable=self.transcription_var, wraplength=380, fg="blue")
        self.transcription_label.pack(pady=10)

        self.recording = False
        self.audio_queue = queue.Queue()

        self.keyboard_controller = keyboard.Controller()
        self.listener = keyboard.Listener(on_press=self.on_press, on_release=self.on_release)
        self.listener.start()

    def on_press(self, key):
        if key == keyboard.Key.alt_l and not self.recording:
            self.recording = True
            self.status_var.set("Recording...")
            self.transcription_var.set("")
            self.audio_queue = queue.Queue() # Clear previous audio data
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
                    self.status_var.set("Press and hold Left Option to start recording...")
                    if transcribed_text:
                        self.keyboard_controller.type(transcribed_text)
                else:
                    self.status_var.set(f"Error: {response.status_code} - {response.text}")
        except Exception as e:
            self.status_var.set(f"Error: {e}")

if __name__ == "__main__":
    app = VoiceTranscriber()
    app.mainloop()
