import platform
import subprocess
import threading
import tkinter as tk
from tkinter import Button, PhotoImage, Label, Frame
from tkinter import ttk
from PIL import Image, ImageTk


class BypassOpen(Frame):
    def __init__(self, master, width, height, background, manager):
        super().__init__(master)
        # self.root = master
        self.width = width
        self.height = height
        self.background = background
        self.manager = manager
        self.bg_photo = None

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
        self.frame = ttk.Frame(self.canvas, style="Purple.TFrame")
        self.canvas.create_window(
            10,
            self.height - 10,
            window=self.frame,
            anchor="sw"
        )

        self.text_box = tk.Text(
            self.frame,
            borderwidth=0,
            highlightthickness=0,
            wrap="word",
            width=80,
            height=25,
            font=("Calibri", 15),
            bg="purple",     
            fg="white",     
            insertbackground="white"  
        )
        self.text_box.pack(fill="both", padx=0, pady=0)
        self.text_box.tag_configure("bold", font=("Calibri", 15, "bold"))

        self.button = Button(
            self.canvas,
            text="Continue >",          
            command=self.jump_to_bypass_on,
            borderwidth=0,
            relief="flat",              
            bg="white",               
            fg="black",                
            font=("Arial", 12)         
        )
        self.button.place(x=1450, y=850) 

        self.switch_open()
        self.ping_one_to_three()

    def jump_to_bypass_on(self):
        self.manager.show_page("bypass_on")
    
    def switch_open(self):
        def open():
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

    def ping_one_to_three(self):
        def run_ping():
            target = "192.168.1.3"
            count = 4
            cmd = f"ping -n {count} {target}"

            self.after(0, lambda: [
                self.text_box.insert(tk.END, "Pinging PNSR-5001 on orange wire...\n"),
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
            
            self.after(0, lambda: [
                self.text_box.insert(tk.END, "\n[Ping Completed]\n"),
                self.text_box.see(tk.END),
                self.text_box.config(state=tk.DISABLED)  
            ])
        
        threading.Thread(target=run_ping, daemon=True).start()

    def update_text_box(self, text):
        self.text_box.config(state=tk.NORMAL)  
        self.text_box.insert(tk.END, text)
        self.text_box.see(tk.END)