import tkinter as tk
from tkinter import Button, PhotoImage, Label, Frame
from tkinter import ttk
from PIL import Image, ImageTk

class BypassMain(Frame):
    def __init__(self, master, width, height, background, manager):
        super().__init__(master)
        #self.root = master
        self.width = width
        self.height = height
        self.background = background
        self.manager = manager
        self.bg_photo = None

        #self.root.geometry("%dx%d" % (width, height))

        # Load the background image
        bg_image = Image.open(background)
        bg_image = bg_image.resize((width, height), Image.LANCZOS)
        bg_photo = ImageTk.PhotoImage(bg_image)
        self.bg_photo = bg_photo

        # Create a canvas to place the background image
        self.canvas = tk.Canvas(self, width=width, height=height)
        self.canvas.pack(fill="both", expand=True)
        self.canvas.create_image(0, 0, image=bg_photo, anchor="nw")

        # frame 
        self.frame = ttk.Frame(self.canvas, style="Purple.TFrame")
        self.canvas.create_window(
            10,
            self.height - 10,
            window=self.frame,
            anchor="sw"
        )

        # self.text_box = tk.Text(
        #     self.frame,
        #     borderwidth=0,
        #     highlightthickness=0,
        #     wrap="word",
        #     width=80,
        #     height=25,
        #     font=("Calibri", 15),
        #     bg="purple",     
        #     fg="white",     
        #     insertbackground="white"  
        # )
        # self.text_box.pack(fill="both", padx=0, pady=0)
        # self.text_box.tag_configure("bold", font=("Calibri", 15, "bold"))

        button_image = Image.open("images/continue_button.png").resize((280,90))
        self.button_image = ImageTk.PhotoImage(button_image) 
        self.button = Button(
            self.canvas,
            # text="Continue >",      
            image=self.button_image,    
            command=self.jump_to_bypass_normal,
            borderwidth=0,
            highlightthickness=0,
            relief="flat",              
            bg="#f8fafa",               
            fg="black",                
            font=("Arial", 12)         
        )
        self.button.place(x=1580, y=900) 

        #self.root.mainloop()

    def jump_to_bypass_normal(self):
        self.manager.show_page("bypass_normal")

    # def close_window(self):
    #     self.master.destroy()