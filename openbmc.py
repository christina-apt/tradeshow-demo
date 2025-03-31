import tkinter as tk
from PIL import Image, ImageTk
import webview

class OpenBMC(tk.Frame):
    def __init__(self, master, background="background1.jpg"):
        self.root = master
        self.root.geometry("1024x768")
        self.root.title("Embedded Web Browser")

        # Load the background image
        # self.load_background(background)

        # Automatically load the browser when the OpenBMC class is called
        self.load_browser()

    # def load_background(self, background):
    #     # Load and display the background image
    #     bg_image = Image.open(background)
    #     bg_image = bg_image.resize(1600, 900)
    #     bg_photo = ImageTk.PhotoImage(bg_image)

    #     # Create a canvas to place the background image
    #     canvas = tk.Canvas(self.root, width=1024, height=768)
    #     canvas.pack(fill="both", expand=True)
    #     canvas.create_image(0, 0, image=bg_photo, anchor="nw")

    #     # Keep a reference to the image to prevent it from being garbage collected
    #     self.bg_photo = bg_photo

    def load_browser(self):
        # Open google.com inside a frameless PyWebView window
        window = webview.create_window('Simple browser', 'https://pywebview.flowrl.com/hello')
        webview.start()