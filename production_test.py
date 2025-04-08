import tkinter as tk
from tkinter import Button, scrolledtext, Menu, PhotoImage, Label, Frame, ttk
from PIL import Image, ImageTk

class ProductionTest(tk.Frame):
    def __init__(self, master, background="images/production_bg.png"):
        width=1600 #root.winfo_screenwidth() 
        height=900 #root.winfo_screenheight()
        #setting tkinter window 
        self.root.geometry("%dx%d" % (width, height))
        self.root.title("Production Test")

        icon = PhotoImage(file="portwell_logo.png")
        self.root.iconphoto(False, icon)

        bg_image = Image.open(background)
        bg_image.resize((width,height))
        bg_photo = ImageTk.PhotoImage(bg_image)
