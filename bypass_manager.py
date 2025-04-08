import tkinter as tk
from PIL import Image, ImageTk
import platform
from tkinter import Frame
from bypass_normal import BypassNormal
from bypass_open import BypassOpen
from bypass_on import BypassOn

class BypassManager(Frame):
    def __init__(self, master):
        self.root = master
        self.current_page = None
        self.width = 1600
        self.height = 900

        self.pages = {
            "bypass_normal": {
                "class": BypassNormal,
                "bg": "background1.jpg",
                "width": self.width,
                "height": self.height,
            },
            "bypass_open": {
                "class": BypassOpen,
                "bg": "background2.jpg",
                "width": self.width,
                "height": self.height,
            },
            "bypass_on": {
                "class": BypassOn,
                "bg": "background3.jpg",
                "width": self.width,
                "height": self.height,
            },
        }
        self.root.title("APT OCP NIC 3.0 Network Test")
        # self.is_windows = platform.system() == 'Linux'
        self.show_page("bypass_normal") 

        # self.root.mainloop()

    def show_page(self, page_name):
        
        page_config = self.pages.get(page_name)
        if not page_config:
            return
        
        if self.current_page:
            self.current_page.destroy()

        PageClass = page_config["class"]
        self.current_page = PageClass(
            master=self.root,
            width=page_config["width"],
            height=page_config["height"],
            background=page_config["bg"],
            manager=self
        )
        self.current_page.pack(fill="both", expand=True)  
