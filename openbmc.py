import tkinter as tk
import tkinterweb

class OpenBMC(tk.Frame):
    def __init__(self, master, background="background1.jpg"):
        super().__init__(master)  # Initialize the parent tk.Frame class
        self.master.geometry("1024x768")
        self.master.title("Embedded Web Browser")
        self.load_browser()

    def load_browser(self):
        # Create an HtmlFrame to load the web page
        frame = tkinterweb.HtmlFrame(self.master)
        frame.load_website("https://200.200.200.102")  # Load the desired URL
        frame.pack(fill="both", expand=True)  # Expand the frame to fill the window
