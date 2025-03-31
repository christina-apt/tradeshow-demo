import tkinter as tk
from PIL import Image, ImageTk
import os

class ImageCarousel:
    def __init__(self, master, image_folder, delay=2000):
        self.master = master
        self.image_folder = image_folder
        self.delay = delay
        self.image_files = [f for f in os.listdir(image_folder) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp'))]
        self.current_index = 0
        self.image_labels = []

        if not self.image_files:
            tk.Label(master, text="No images found in the specified folder.").pack()
            return

        self.canvas_width = 1600 
        self.canvas_height = 900
        self.canvas = tk.Canvas(master, width=self.canvas_width, height=self.canvas_height)
        self.canvas.pack()

        self.load_images()
        self.display_image()
        self.auto_advance()

    def load_images(self):
         for file in self.image_files:
            image_path = os.path.join(self.image_folder, file)
            image = Image.open(image_path)
            image = image.resize((1600, 900), Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(image)
            self.image_labels.append(photo)

    def display_image(self):
        if self.image_labels:
            self.canvas.delete("all")
            self.canvas.create_image(self.canvas_width / 2, self.canvas_height / 2, image=self.image_labels[self.current_index], anchor=tk.CENTER)

    def next_image(self):
        self.current_index = (self.current_index + 1) % len(self.image_labels)
        self.display_image()

    def prev_image(self):
         self.current_index = (self.current_index - 1) % len(self.image_labels)
         self.display_image()

    def auto_advance(self):
        if self.image_labels:
            self.next_image()
            self.master.after(self.delay, self.auto_advance)