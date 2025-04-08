import tkinter as tk
from tkinter import Button, scrolledtext, Menu, PhotoImage, Label, Frame, ttk
from PIL import Image, ImageTk

class ProductionTest(tk.Frame):
    def __init__(self, master, background="images/production_bg.png"):
        width=1920 #root.winfo_screenwidth() 
        height=1016 #root.winfo_screenheight()
        #setting tkinter window 
        master.geometry("%dx%d" % (width, height))
        master.title("Production Test")

        icon = PhotoImage(file="portwell_logo.png")
        master.iconphoto(False, icon)

        bg_image = Image.open(background)
        resized_bg_image = bg_image.resize((width,height))
        bg_photo = ImageTk.PhotoImage(resized_bg_image)

        canvas = tk.Canvas(master, width=width, height=height)
        canvas.pack(fill="both", expand="True")
        canvas.create_image(0, 0, image=bg_photo, anchor="nw")
