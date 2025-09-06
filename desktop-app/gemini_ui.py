import tkinter as tk
from tkinter import ttk

class GeminiUI(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Gemini Response")
        
        # Set window dimensions
        window_width = 400
        window_height = 300

        # Get screen dimensions
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()

        # Calculate position for bottom-right corner
        x_position = screen_width - window_width
        y_position = screen_height - window_height - 100 # A little bit of padding from bottom

        self.geometry(f"{window_width}x{window_height}+{x_position}+{y_position}")

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

        self.continue_conversation_var = tk.BooleanVar()
        self.continue_conversation_check = ttk.Checkbutton(
            self,
            text="Continue Conversation",
            variable=self.continue_conversation_var
        )
        self.continue_conversation_check.grid(row=4, column=0, padx=10, pady=10, sticky="w")

    def show_question(self, text):
        self.question_var.set(text)
        self.answer_var.set("...") # Clear previous answer and indicate waiting
        self.deiconify() # Show the window

    def show_response(self, text):
        self.answer_var.set(text)
