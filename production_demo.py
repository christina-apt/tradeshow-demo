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

class ProductionDemo(Frame):
    
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
        self.root.title("Production Demo")

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
        self.text_label = tk.Label(canvas, text="Production Demo", 
                      font=("Arial", 14, "bold"), 
                      bg="royalblue", fg="white", 
                      padx=20, pady=10, 
                      borderwidth=2, relief="solid")

        # Put the Title in the middle
        self.text_label.pack(pady=20)

        # frame 
        self.frame1 = ttk.Frame(canvas,style="RoundedFrame", padding=10)
        self.frame1.pack(side=tk.LEFT,pady=(200,15), padx=(25,0))
        self.text_box = tk.Text(self.frame1, borderwidth=0, highlightthickness=0, wrap="word",
                        width=150, height=130, font=("Courier", 12))
        self.text_box.pack(fill="both", padx=10, pady=10)
        self.text_box.tag_configure("bold", font=("Calibri", 25, "bold"))

        # auto update
        self.root.bind("<FocusIn>", lambda event: self.update_terminal()) 
        self.update_terminal()
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

        self.right_frame = ttk.Frame(canvas, style="RoundedFrame")
        self.right_frame.pack(side=tk.RIGHT,pady=(30,15), padx=(0,40))

        # Create a scrolled text box to display the output
        self.output_label = Label(self.right_frame, text="Test Console", font=("Calibri", 14, "bold"), bg="white")
        self.output_label.pack(anchor="nw", pady=(10,0), padx=(15,5))
        self.output_text = scrolledtext.ScrolledText(self.right_frame, wrap=tk.WORD, width=103, height=60, bg="black", fg="white")
        self.output_text.pack(expand=False, padx=(5,10), pady=(5,7))

        # Run the Tkinter event loop
        self.root.mainloop()

    def update_terminal(self):
        print("pass update terminal")
        try:
            with open("production_test_results.json", "r") as f:
                data = json.load(f)

            self.text_box.config(state=tk.NORMAL)
            self.text_box.delete(1.0, tk.END) 

            for key, value in data["metadata"].items():
                self.text_box.insert(tk.END, f"{key}: {value}\n", "bold")

            self.text_box.tag_configure("blue", foreground="blue")
            self.text_box.insert(tk.END, "---------------------------------AUTOMATED TEST RESULTS--------------------------------\n")
            self.text_box.insert(tk.END, "<NAME>                                                     <RESULT>\n", "blue")
            
            # show the test result
            for item in data["results"]:
                color = "green" if item["result"] == "PASS" else "red"
                self.text_box.insert(tk.END, f"{item['name']:60} {item['result']}\n", color)

            self.text_box.insert(tk.END, "---------------------------------------------------------------------------------------\n")
            self.text_box.insert(tk.END, "\nTOTAL RESULT: " + data["total_result"], "red" if data["total_result"] == "FAILED" else "green")

            # set the color
            self.text_box.tag_configure("bold", font=("Courier", 12, "bold"))
            self.text_box.tag_configure("red", foreground="red")
            self.text_box.tag_configure("green", foreground="green")

            self.text_box.config(state=tk.DISABLED)

        except FileNotFoundError:
            self.text_box.config(state=tk.NORMAL)
            self.text_box.delete(1.0, tk.END)
            self.text_box.insert(tk.END, "Waiting for test results...\n")
            self.text_box.config(state=tk.DISABLED)

        self.root.after(5000, self.update_terminal)