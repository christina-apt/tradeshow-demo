import os
import re
import time
import platform
import tkinter as tk
from tkinter import Button, scrolledtext, Menu, PhotoImage, Label, Frame, ttk
from PIL import Image, ImageTk
import subprocess
import threading
from datetime import datetime
from tabulate import tabulate
import json

class Bypass5000App(Frame):
    
    def __init__(self, master, background="background1.jpg"):

        self.slot = "0x00"
        with open('./global.json') as f:
            self.globalVariable = json.load(f)

        self.current_bg = background
        self.bg_images = {
            "page1": "background1.jpg",
            "page2": "page 2.png",
            "page3": "page 3.png"
        }

        self.is_windows = platform.system() == 'Windows'
        # Create the main window
        self.root = master

        # resolution
        width=1600 #root.winfo_screenwidth() 
        height=900 #root.winfo_screenheight()
        #setting tkinter window size
        self.root.geometry("%dx%d" % (width, height))
        self.root.title("APT OCP NIC 3.0 Network Test")

        # Load the icon image
        icon = tk.PhotoImage(file="portwell_logo.png")
        self.root.iconphoto(False, icon)


        # Load the background image
        bg_image = Image.open(background)
        bg_image = bg_image.resize((width, height), Image.LANCZOS)
        bg_photo = ImageTk.PhotoImage(bg_image)

        # Create a canvas to place the background image
        canvas = tk.Canvas(self.root, width=width, height=height)
        canvas.pack(fill="both", expand=True)
        canvas.create_image(0, 0, image=bg_photo, anchor="nw")

        # Title
        self.text_label = tk.Label(canvas, text="Bypass Demo", 
                      font=("Arial", 14, "bold"), 
                      bg="royalblue", fg="white", 
                      padx=20, pady=10, 
                      borderwidth=2, relief="solid")

        # Put the Title in the middle
        self.text_label.pack(pady=20)
        
        # frame 
        self.frame = ttk.Frame(canvas, style="Purple.TFrame", padding=10)
        style = ttk.Style()
        style.configure("Purple.TFrame", background="purple")
        self.frame.pack_forget()
        self.text_box = tk.Text(
            self.frame,
            borderwidth=0,
            highlightthickness=0,
            wrap="word",
            width=60,
            height=35,
            font=("Calibri", 15),
            bg="purple",     
            fg="white",     
            insertbackground="white"  
        )
        self.text_box.pack(fill="both", padx=10, pady=10)
        self.text_box.tag_configure("bold", font=("Calibri", 15, "bold"))

        # Button 1, 2, 3
        self.button = Button(
            canvas,
            text="Continue >",          
            command=self.toggle_interface,
            borderwidth=0,
            relief="flat",              
            bg="white",               
            fg="black",                
            font=("Arial", 12)         
        )
        self.button.place(x=1450, y=850) 
        
        # text status
        # self.left_frame = ttk.Frame(canvas,style="RoundedFrame", padding=10)
        # self.left_frame.pack(side=tk.TOP, anchor="ne", pady=(30,0), padx=(0,40))
        # self.test_output_label = Label(self.left_frame, text="Test Status", font=("Calibri", 14, "bold"), bg="white")
        # self.test_output_label.pack(anchor="nw", pady=(5,0), padx=(10,5))
        # self.text_left_box = tk.Text(self.left_frame, borderwidth=0, highlightthickness=0, wrap="word",
        #                 width=120, height=1, font=("Calibri", 14))
        # self.text_left_box.pack(fill="both", expand=True, padx=5, pady=10)
        # self.text_left_box.tag_configure("bold", font=("Calibri", 14, "bold"))
        # self.text_left_box.tag_configure("red", foreground="red")
        # self.text_left_box.tag_configure("green", foreground="green")


        # Create a button to execute command
        # self.button = Button(canvas, text="", command=self.run_save_fru, font=("Calibri", 10))

        # Create a menu bar
        self.menu_bar = Menu(canvas)
        self.root.config(menu=self.menu_bar)
        self.menu_bar.add_command(label="Start Tests", command=self.run_all)
        self.menu_bar.add_command(label="PCIe Test", command=self.run_pcie)
        self.menu_bar.add_command(label="Connectivity Test", command=self.run_ping)
        self.menu_bar.add_command(label="Bandwidth Test", command=self.run_iperf)
        self.menu_bar.add_command(label="Read FRU", command=self.run_read_fru)

        self.right_frame = ttk.Frame(canvas, style="RoundedFrame")
        self.right_frame.pack(side=tk.RIGHT,pady=(30,15), padx=(0,40))

        # Create a scrolled text box to display the output
        self.output_label = Label(self.right_frame, text="Test Console", font=("Calibri", 14, "bold"), bg="white")
        self.output_label.pack(anchor="nw", pady=(10,0), padx=(15,5))
        self.output_text = scrolledtext.ScrolledText(self.right_frame, wrap=tk.WORD, width=103, height=60, bg="black", fg="white")
        self.output_text.pack(expand=False, padx=(5,10), pady=(5,7))

        self.tests = [(0, self.delete_menu),(30000,self.run_pcie), (25000,self.run_ping), (50000,self.run_iperf), (10000,self.run_read_fru), (0,self.quit)]

        # self.root.after(100, self.run_initial_commands)

        # Run the Tkinter event loop
        self.root.mainloop()
    
    def run_command(self, index):
        self.start_terminal(index, "ls")
        # self.start_terminal(index, "echo 'Hello, Terminal!'")


    def start_terminal(self, index, command):
        def run():
            print(f"Running command: {command} in terminal {index}")
            process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE, text=True)

            stdout, stderr = process.communicate()

            self.text_boxes[index].config(state=tk.NORMAL)  # allow to write
            self.text_boxes[index].delete(1.0, tk.END)  # Delete previous contents
            self.text_boxes[index].insert(tk.END, stdout)
            self.text_boxes[index].see(tk.END)  # rolling to the bottom
            self.text_boxes[index].config(state=tk.DISABLED) # set the writing to disable
            
            if stderr:
                print(f"Error in terminal {index}: {stderr}")

        thread = threading.Thread(target=run, daemon=True)
        thread.start()

    def on_continue_clicked(self):
        self.frame.pack(side=tk.LEFT,pady=(175,15), padx=(25,0))
        self.ping_internet()

    def ping_internet(self):
        def run_ping():
            target = "google.com"
            count = 4
            if self.is_windows:
                cmd = f"ping -n {count} {target}"
            else:
                cmd = f"ping -c {count} {target}"
            
            process = subprocess.Popen(cmd, shell=True, 
                                     stdout=subprocess.PIPE, 
                                     stderr=subprocess.PIPE,
                                     universal_newlines=True)
            
            while True:
                output = process.stdout.readline()
                if output == '' and process.poll() is not None:
                    break
                if output:
                    self.root.after(0, self.update_text_box, output)
            
            process.poll()
        
        threading.Thread(target=run_ping, daemon=True).start()
    
    def update_text_box(self, text):
        self.text_box.config(state=tk.NORMAL)
        self.text_box.insert(tk.END, text)
        self.text_box.see(tk.END)  
        self.text_box.config(state=tk.DISABLED)

    def toggle_interface(self):
        # clear current content
        self.text_box.delete(1.0, tk.END)

        # switch the bg 
        if self.current_bg == self.bg_images["page1"]:
            new_bg = self.bg_images["page2"]
            new_command = "ping 8.8.8.8" 
        else:
            new_bg = self.bg_images["page1"]
            new_command = "ping google.com"
        
        # update bg
        self.update_background(new_bg)
        self.current_bg = new_bg

        self.execute_command(new_command)

    def update_background(self, image_path):
        bg_image = Image.open(image_path)
        bg_image = bg_image.resize((1600, 900), Image.LANCZOS)
        self.bg_photo = ImageTk.PhotoImage(bg_image)  
        self.canvas.itemconfig(self.bg_item, image=self.bg_photo)
    
    def execute_command(self, command):
        threading.Thread(target=lambda: self.run_command_in_frame(command), daemon=True).start()
    
    def run_command_in_frame(self, command):
        process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, text=True)
        for line in iter(process.stdout.readline, ''):
            self.text_box.insert(tk.END, line)
            self.text_box.see(tk.END)

    def action1(self):
        print("Button 1 clicked!")
    
