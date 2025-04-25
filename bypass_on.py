import platform
import subprocess
import threading
import queue
import tkinter as tk
from tkinter import Button, PhotoImage, Label, Frame
from tkinter import ttk
from PIL import Image, ImageTk

class BypassOn(Frame):
    def __init__(self, master, width, height, background, manager):
        super().__init__(master)
        # self.root = master
        self.width = width
        self.height = height
        self.background = background
        self.manager = manager
        self.bg_photo = None

        self.output_queue = queue.Queue()

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

        button_image = Image.open("images/continue_button.png").resize((280,90))
        self.button_image = ImageTk.PhotoImage(button_image) 
        self.button = Button(
            self.canvas,
            # text="Continue >",      
            image=self.button_image,    
            command=self.jump_to_bypass_off,
            borderwidth=0,
            highlightthickness=0,
            relief="flat",              
            bg="#f8fafa",               
            fg="black",                
            font=("Arial", 12)         
        )
        self.button.place(x=1580, y=900) 

        self.switch_bypass()
        self.after(1000, self.ping_one_to_three_then_one_to_two)

        self.process_output()

        #self.root.mainloop()
    
    def process_output(self):
        try:
            while True:
                line = self.output_queue.get_nowait()
                self.text_box.config(state=tk.NORMAL)
                self.text_box.insert(tk.END, line)
                self.text_box.see(tk.END)
                self.text_box.config(state=tk.DISABLED)
        except queue.Empty:
            pass
        self.text_box.after(100, self.process_output)
    
    def jump_to_bypass_off(self):
        self.manager.show_page("bypass_off")

    def switch_bypass(self):
        def bypass():
            cmd = f"echo \"111111\" | sudo -S python /home/apt/Documents/test/bypass_on.py"
            
            self.after(0, lambda: [
                self.text_box.config(state=tk.NORMAL),
                self.text_box.insert(tk.END, "Changing bypass pair to bypass mode...\n"),
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
        
            process.wait()
        
        threading.Thread(target=bypass, daemon=True).start()

    def ping_one_to_three_then_one_to_two(self):
        def run_ping():
           
            target = "192.168.1.3"
            source = "192.168.1.1"
            count = 4
            cmd = f"ping -n {count} {target}" if self.is_windows else f"ping -c {count} -I {source} {target}"

            self.after(0, lambda: [
                self.text_box.config(state=tk.NORMAL),
                self.text_box.insert(tk.END, "Pinging PNSR-5000 on orange wire...\n"),
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
                self.output_queue.put(line)
        
            process.wait()

            self.after(0, lambda: [
                self.text_box.config(state=tk.NORMAL),
                self.text_box.insert(tk.END, "\n[Ping Completed]\n"),
                self.text_box.see(tk.END),
                self.text_box.config(state=tk.DISABLED)
            ])

            self.after(1000, lambda: [
                self.ping_one_to_two()
            ])
        
        threading.Thread(target=run_ping, daemon=True).start()

    def ping_one_to_two(self):
        def run_ping():
            target = "192.168.1.2"
            source = "192.168.1.1"
            count = 4
            cmd = f"ping -n {count} {target}" if self.is_windows else f"ping -c {count} -I {source} {target}"

            self.after(0, lambda: [
                self.text_box.config(state=tk.NORMAL),
                self.text_box.insert(tk.END, "Pinging PNSR-5001 on orange wire and back on pink wire...\n"),
                self.text_box.see(tk.END) 
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
                self.text_box.config(state=tk.NORMAL),
                self.text_box.insert(tk.END, "\n[Ping Completed]\n"),
                self.text_box.see(tk.END),
                self.text_box.config(state=tk.DISABLED)  
            ])
        
        threading.Thread(target=run_ping, daemon=True).start()

    def update_text_box(self, text):
        self.text_box.config(state=tk.NORMAL)  
        self.text_box.insert(tk.END, text)
        self.text_box.see(tk.END)

    def close_window(self):
        self.master.destroy()