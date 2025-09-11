import tkinter as tk
from tkinter import ttk

class GeminiUI(tk.Toplevel):
    def __init__(self, parent, send_callback):
        super().__init__(parent)
        self.title("Gemini Response")
        self.send_callback = send_callback
        
        # Set window dimensions
        window_width = 400
        window_height = 400

        # Get screen dimensions
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()

        # Calculate position for bottom-right corner
        x_position = screen_width - window_width
        y_position = screen_height - window_height - 100 # A little bit of padding from bottom

        self.geometry(f"{window_width}x{window_height}+{x_position}+{y_position}")

        self.attributes("-alpha", 0.5)
        self.attributes("-topmost", True)

        self.grid_rowconfigure(3, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Question Area
        self.question_label = ttk.Label(self, text="Your Question:", font=("Arial", 12, "bold"))
        self.question_label.grid(row=0, column=0, padx=10, pady=(10, 0), sticky="w")
        
        self.question_text = tk.Text(self, wrap=tk.WORD, font=("Arial", 14), height=3, width=40)
        self.question_text.grid(row=1, column=0, padx=10, pady=5, sticky="nswe")

        # Answer Area
        self.answer_label = ttk.Label(self, text="Gemini's Answer:", font=("Arial", 12, "bold"))
        self.answer_label.grid(row=2, column=0, padx=10, pady=(10, 0), sticky="w")

        self.answer_text = tk.Text(self, wrap=tk.WORD, font=("Arial", 14), foreground="green", height=10, width=40)
        self.answer_text.grid(row=3, column=0, padx=10, pady=5, sticky="nswe")
        
        # Make the text selectable and copiable but not editable
        self.answer_text.bind("<Key>", lambda e: "break")

        # Add a scrollbar
        scrollbar = ttk.Scrollbar(self, command=self.answer_text.yview)
        scrollbar.grid(row=3, column=1, sticky="ns")
        self.answer_text.config(yscrollcommand=scrollbar.set)

        # Send button
        self.send_button = ttk.Button(self, text="Send", command=self.send_message)
        self.send_button.grid(row=4, column=0, padx=10, pady=10, sticky="e")

        self.continue_conversation_var = tk.BooleanVar()
        self.continue_conversation_check = ttk.Checkbutton(
            self,
            text="Continue Conversation",
            variable=self.continue_conversation_var
        )
        self.continue_conversation_check.grid(row=5, column=0, padx=10, pady=10, sticky="w")

    def show_question(self, text):
        self.question_text.delete("1.0", tk.END)
        self.question_text.insert(tk.END, text)
        self.answer_text.delete("1.0", tk.END)
        self.answer_text.insert(tk.END, "...")
        self.deiconify() # Show the window

    def show_response(self, text):
        self.answer_text.delete("1.0", tk.END)
        self.answer_text.insert(tk.END, text)

    def send_message(self):
        message = self.question_text.get("1.0", tk.END).strip()
        if message:
            self.send_callback(message)
