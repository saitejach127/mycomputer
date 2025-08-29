import tkinter as tk
from tkinter import ttk

class GeminiUI(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Gemini Response")
        self.geometry("400x300+1200+30")  # Position top-right

        self.attributes("-alpha", 0.5)
        self.attributes("-topmost", True)

        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Question Area
        self.question_label = ttk.Label(self, text="Your Question:", font=("Arial", 12, "bold"))
        self.question_label.grid(row=0, column=0, padx=10, pady=(10, 0), sticky="w")
        
        self.question_var = tk.StringVar()
        question_text = ttk.Label(self, textvariable=self.question_var, wraplength=380, font=("Arial", 14))
        question_text.grid(row=1, column=0, padx=10, pady=5, sticky="nswe")

        # Answer Area
        self.answer_label = ttk.Label(self, text="Gemini's Answer:", font=("Arial", 12, "bold"))
        self.answer_label.grid(row=2, column=0, padx=10, pady=(10, 0), sticky="w")

        self.answer_var = tk.StringVar()
        answer_text = ttk.Label(self, textvariable=self.answer_var, wraplength=380, font=("Arial", 14), foreground="green")
        answer_text.grid(row=3, column=0, padx=10, pady=5, sticky="nswe")

    def show_question(self, text):
        self.question_var.set(text)
        self.answer_var.set("...") # Clear previous answer and indicate waiting
        self.deiconify() # Show the window

    def show_response(self, text):
        self.answer_var.set(text)
