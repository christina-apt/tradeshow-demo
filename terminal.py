import tkinter as tk
import platform
from tkinter import Toplevel, ttk
from PIL import Image, ImageTk
import testgui
from testgui import TestGUI
from bypass_test import BypassTest
from bypass_test_new import Bypass5000App
#from openbmc import OpenBMC

def on_button1_click():
    new_window = Toplevel(root)
    app = BypassTest(new_window, "background1.jpg")

def on_button2_click():
    new_window = Toplevel(root)
    app = BypassTest(new_window, "background2.jpg")

def on_button3_click():
    new_window = Toplevel(root)
    app = BypassTest(new_window, "background3.jpg")

def on_button4_click():
    new_window = Toplevel(root)
    app = Bypass5000App(new_window, "background4.jpg")

# Create the main window
root = tk.Tk()
#if platform.system() == "Windows":
#    root.state('zoomed')
#else:
#    root.attributes('-zoomed', True)
#root.title("GUI with Background Image")
#width = root.winfo_screenwidth() 
#height = root.winfo_screenheight()
#setting tkinter window size
width=1600
height=900
root.geometry("%dx%d" % (width, height))
root.title("American Portwell Technology | RSAC 2025")

style = ttk.Style()
borderImage = tk.PhotoImage("borderImage", file="image.gif")

style.element_create("RoundedFrame","image", borderImage,border=16, sticky="nsew")
style.layout("RoundedFrame",[("RoundedFrame", {"sticky": "nsew"})])

# Load the background image
bg_image = Image.open("1.png")
bg_image.resize((width,height))
bg_photo = ImageTk.PhotoImage(bg_image)

# Create a canvas to place the background image
canvas = tk.Canvas(root, width=width, height=height)
canvas.pack(fill="both", expand="True")
canvas.create_image(0, 0, image=bg_photo, anchor="nw")

# Load the button images
button1_image = Image.open("ducks.jpg").resize((400,150)) # Production Test
button1_photo = ImageTk.PhotoImage(button1_image)

button2_image = Image.open("ducks.jpg").resize((400,150)) 
button2_photo = ImageTk.PhotoImage(button2_image)

button3_image = Image.open("ducks.jpg").resize((400,150))
button3_photo = ImageTk.PhotoImage(button3_image)

button4_image = Image.open("ducks.jpg").resize((400,150)) # Network Test
button4_photo = ImageTk.PhotoImage(button4_image)

# Create buttons with the images
button1 = tk.Button(root, image=button1_photo, command=on_button1_click, highlightthickness = 5, bd = 0, activebackground="#CBC3E3", bg='#CBC3E3')
button2 = tk.Button(root, image=button2_photo, command=on_button2_click, highlightthickness = 5, bd = 0, activebackground="#CBC3E3", bg='#CBC3E3')
button3 = tk.Button(root, image=button3_photo, command=on_button3_click, highlightthickness = 5, bd = 0, activebackground="#CBC3E3", bg='#CBC3E3')
button4 = tk.Button(root, image=button4_photo, command=on_button4_click, highlightthickness = 5, bd = 0, activebackground="#CBC3E3", bg='#CBC3E3')

# Place the buttons on the canvas
canvas.create_window(bg_photo.width()//2 + 15, bg_photo.height()-150, anchor="center", window=button1)
canvas.create_window(bg_photo.width()//2 + 465, bg_photo.height()-150, anchor="center", window=button2)
canvas.create_window(bg_photo.width()//2 + 15, bg_photo.height()-350, anchor="center", window=button3)
canvas.create_window(bg_photo.width()//2 + 465, bg_photo.height()-350, anchor="center", window=button4)

# Start the Tkinter event loop
root.mainloop()


'''
import tkinter as tk
from tkinter import scrolledtext

def execute_command():
    command = entry.get()
    if command:
        output_text.insert(tk.END, f"> {command}\n", "command")
        # Here you can add logic to execute the command and display the result
        # For now, we'll just echo the command
        output_text.insert(tk.END, f"Executed: {command}\n", "output")
        entry.delete(0, tk.END)

# Create the main window
root = tk.Tk()
root.title("Terminal-like GUI")

# Create a scrolled text widget for output with black background and green text
output_text = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=80, height=20, bg="black", fg="green")
output_text.pack(padx=10, pady=10)

# Create a tag for command text
output_text.tag_config("command", foreground="green")

# Create a tag for output text
output_text.tag_config("output", foreground="white")

# Create an entry widget for input with black background and green text
entry = tk.Entry(root, width=80, bg="black", fg="green", insertbackground="green")
entry.pack(padx=10, pady=(0, 10))
entry.bind("<Return>", lambda event: execute_command())

# Create a button to execute the command
execute_button = tk.Button(root, text="Execute", command=execute_command, bg="black", fg="green")
execute_button.pack(pady=(0, 10))

# Start the Tkinter event loop
root.mainloop()
'''

'''

'''
