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

        match background:
            case "page 2.png":
                self.globalVariable = self.globalVariable['nic1']
                self.slot = "0x00"
                self.fru = "values1.txt"
            case "page 3.png":
                self.globalVariable = self.globalVariable['nic2']
                self.slot = "0x01"
                self.fru = "values2.txt"
            case "page 4.png":
                self.globalVariable = self.globalVariable['nic3']  
                self.slot = "0x02"
                self.fru = "values3.txt"     

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
        bg_image.resize((width,height))
        bg_photo = ImageTk.PhotoImage(bg_image)

        # Create a canvas to place the background image
        canvas = tk.Canvas(self.root, width=width, height=height)
        canvas.pack(fill="both", expand=True)
        canvas.create_image(0, 0, image=bg_photo, anchor="nw")

        self.progress_bar = PhotoImage(file="test_0.png")

        self.progress_bar_label = tk.Label(canvas, image=self.progress_bar, bd=0)
        self.progress_bar_label.pack(side=tk.BOTTOM, pady=(0,15))

        # Load Pictures 
        # need to change to real pnc card picture
        self.img1 = ImageTk.PhotoImage(Image.open("ducks.jpg").resize((100, 80)))
        self.img2 = ImageTk.PhotoImage(Image.open("ducks.jpg").resize((100, 80)))
        self.img3 = ImageTk.PhotoImage(Image.open("ducks.jpg").resize((100, 80)))    

        # Title
        self.text_label = tk.Label(canvas, text="Bypass Demo", 
                      font=("Arial", 14, "bold"), 
                      bg="royalblue", fg="white", 
                      padx=20, pady=10, 
                      borderwidth=2, relief="solid")

        # 放置在窗口顶部居中
        self.text_label.pack(pady=20)

        # create Frame to store 3 terminal
        self.frames = []
        self.text_boxes = []

        # termimal content
        self.processes = [] 

        for i in range(3):
            frame = ttk.Frame(canvas, style="RoundedFrame", padding=10)
            frame.pack(side=tk.LEFT, pady=(300, 15), padx=(25, 0) if i < 2 else (25, 25))
            self.frames.append(frame)
            
            text_box = tk.Text(frame, borderwidth=0, highlightthickness=0, wrap="word", width=22, height=15, font=("Calibri", 25))
            text_box.config(state=tk.DISABLED)
            text_box.pack(fill="both", padx=10, pady=10)
            text_box.tag_configure("bold", font=("Calibri", 25, "bold"))
            self.text_boxes.append(text_box)

        # # frame 1 
        # self.frame1 = ttk.Frame(canvas,style="RoundedFrame", padding=10)
        # self.frame1.pack(side=tk.LEFT,pady=(300,15), padx=(25,0))
        # self.text_box = tk.Text(self.frame1, borderwidth=0, highlightthickness=0, wrap="word", width=22, height=15, font=("Calibri", 25))
        # self.text_box.pack(fill="both", padx=10, pady=10)
        # self.text_box.tag_configure("bold", font=("Calibri", 25, "bold"))

        # # frame 2
        # self.frame2 = ttk.Frame(canvas,style="RoundedFrame", padding=10)
        # self.frame2.pack(side=tk.LEFT,pady=(300,15), padx=(25,0))
        # self.text_box = tk.Text(self.frame2, borderwidth=0, highlightthickness=0, wrap="word", width=22, height=15, font=("Calibri", 25))
        # self.text_box.pack(fill="both", padx=10, pady=10)
        # self.text_box.tag_configure("bold", font=("Calibri", 25, "bold"))

        # # frame 3
        # self.frame3 = ttk.Frame(canvas,style="RoundedFrame", padding=10)
        # self.frame3.pack(side=tk.LEFT,pady=(300,15), padx=(25,25))
        # self.text_box = tk.Text(self.frame3, borderwidth=0, highlightthickness=0, wrap="word", width=22, height=15, font=("Calibri", 25))
        # self.text_box.pack(fill="both", padx=10, pady=10)
        # self.text_box.tag_configure("bold", font=("Calibri", 25, "bold"))


        # Button 1, 2, 3
        self.button1 = Button(canvas, image=self.img1, command=lambda: self.run_command(0), borderwidth=0)
        self.button1.place(x=250, y=250) 

        self.button2 = Button(canvas, image=self.img2, command=lambda: self.run_command(1), borderwidth=0)
        self.button2.place(x=750, y=250) 

        self.button3 = Button(canvas, image=self.img3, command=lambda: self.run_command(2), borderwidth=0)
        self.button3.place(x=1250, y=250) 
        
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

    # def run_initial_commands(self):
    #     for i in range(3):
    #         self.run_command(i)


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

    def action1(self):
        print("Button 1 clicked!")
    
    def action2(self):
        print("Button 2 clicked!")

    def action3(self):
        print("Button 3 clicked!")