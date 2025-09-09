
import tkinter as tk
import numpy as np

class WaveformUI(tk.Toplevel):
    def __init__(self, parent, height, bg='black', corner_radius=20):
        super().__init__(parent)
        self.width = 100  # Reduced width
        self.height = height
        self.bg = bg
        self.corner_radius = corner_radius

        self.overrideredirect(True)
        self.attributes("-alpha", 0.8)
        self.attributes("-topmost", True)

        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x_position = (screen_width // 2) - (self.width // 2)
        y_position = screen_height - self.height - 100  # A little bit of padding from bottom
        self.geometry(f"{self.width}x{self.height}+{x_position}+{y_position}")

        self.canvas = tk.Canvas(self, width=self.width, height=self.height, bg=self.bg, highlightthickness=0)
        self.canvas.pack()

        self.shape = self.create_rounded_rect(0, 0, self.width, self.height, self.corner_radius, fill=self.bg)
        self.canvas.bind("<Configure>", self._on_configure)

        self.dots = []
        self.is_speaking = False
        self.amplitude = 0
        self.dot_positions = []

        self.draw_initial_waveform()
        self.withdraw()

    def create_rounded_rect(self, x1, y1, x2, y2, radius, **kwargs):
        points = [
            x1 + radius, y1,
            x1 + radius, y1,
            x2 - radius, y1,
            x2 - radius, y1,
            x2, y1,
            x2, y1 + radius,
            x2, y1 + radius,
            x2, y2 - radius,
            x2, y2 - radius,
            x2, y2,
            x2 - radius, y2,
            x2 - radius, y2,
            x1 + radius, y2,
            x1 + radius, y2,
            x1, y2,
            x1, y2 - radius,
            x1, y2 - radius,
            x1, y1 + radius,
            x1, y1 + radius,
            x1, y1,
        ]
        return self.canvas.create_polygon(points, **kwargs, smooth=True)

    def _on_configure(self, event):
        self.canvas.delete(self.shape)
        self.shape = self.create_rounded_rect(0, 0, event.width, event.height, self.corner_radius, fill=self.bg)

    def draw_initial_waveform(self):
        self.canvas.delete("all")
        self.shape = self.create_rounded_rect(0, 0, self.width, self.height, self.corner_radius, fill=self.bg)
        self.dots = []
        self.dot_positions = np.linspace(self.width * 0.2, self.width * 0.8, 10)
        
        for x in self.dot_positions:
            y = self.height / 2
            dot = self.canvas.create_oval(x-2, y-2, x+2, y+2, fill='white', outline='')
            self.dots.append(dot)

    def update_waveform(self, indata):
        self.amplitude = np.sqrt(np.mean(indata**2))
        self.is_speaking = self.amplitude > 0.01 

        self.canvas.delete("all")
        self.shape = self.create_rounded_rect(0, 0, self.width, self.height, self.corner_radius, fill=self.bg)
        self.dots = []

        if self.is_speaking:
            num_dots = 20 # Increased for a smoother look when speaking
            self.dot_positions = np.linspace(self.width * 0.1, self.width * 0.9, num_dots)
            
            # Generate a sine-like wave based on amplitude
            frequency = 2 
            y_offsets = self.amplitude * 250 * np.sin(np.linspace(0, frequency * 2 * np.pi, num_dots))

            for i, x in enumerate(self.dot_positions):
                y = self.height / 2 + y_offsets[i]
                size = 1 + self.amplitude * 5
                dot = self.canvas.create_oval(x - size, y - size, x + size, y + size, fill='white', outline='')
                self.dots.append(dot)
        else:
            self.draw_initial_waveform()

    def show(self):
        self.deiconify()

    def hide(self):
        self.withdraw()
