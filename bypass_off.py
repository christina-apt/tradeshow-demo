import platform
import subprocess
import threading
import tkinter as tk
from tkinter import Button, PhotoImage, Label, Frame
from tkinter import ttk
from PIL import Image, ImageTk

class BypassOff(Frame):
    def __init__(self, master, width, height, background, manager):
        super().__init__(master)
        # self.root = master
        self.width = width
        self.height = height
        self.background = background
        self.manager = manager
        self.bg_photo = None

        self.is_windows = platform.system() == 'Windows'

        # self.root.geometry("%dx%d" % (width, height))

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
        self.frame = ttk.Frame(
            self.canvas, 
            style="Purple.TFrame"
        )
        self.canvas.create_window(
            100,
            self.height - 70,
            window=self.frame,
            anchor="sw"
        )

        self.text_box = tk.Text(
            self.frame,
            borderwidth=0,
            highlightthickness=0,
            wrap="word",
            width=65,
            height=20,
            font=("Calibri", 15),
            bg="purple",     
            fg="white",     
            insertbackground="white"  
        )
        self.text_box.pack(fill="both")
        self.text_box.tag_configure("bold", font=("Calibri", 15, "bold"))

        button_image = Image.open("images/return_button.png").resize((237,87))
        self.button_image = ImageTk.PhotoImage(button_image) 
        self.button = Button(
            self.canvas,
            # text="Continue >",      
            image=self.button_image,    
            command=self.close_window,
            borderwidth=0,
            highlightthickness=0,
            relief="flat",              
            bg="#f8fafa",               
            fg="black",                
            font=("Arial", 12)         
        )
        self.button.place(x=1600, y=900) 

        #self.root.mainloop()

    def switch_offstate_bypass(self):
        def offstate_bypass():
            cmd = f"echo \"111111\" | sudo -S python /home/apt/Documents/test/bypass_control.py"
            
            self.after(0, lambda: [
                self.text_box.insert(tk.END, "Changing bypass pair to open mode...\n"),
                self.text_box.see(tk.END),
                self.text_box.config(state=tk.DISABLED)  
            ])

            process = subprocess.Popen(
                cmd,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True,
                bufsize=1, 
                text=True    
            )

            for line in process.stdout:
                self.after(0, self.update_text_box, line)
        
            process.wait()
        
        threading.Thread(target=open, daemon=True).start()

    def close_window(self):
        self.master.destroy()