import tkinter as tk
from PIL import Image, ImageTk
import platform
from tkinter import Frame
from bypass_normal import BypassNormal
from bypass_open import BypassOpen
from bypass_on import BypassOn
from bypass_main import BypassMain
from bypass_off import BypassOff

class BypassManager(Frame):
    def __init__(self, master):
        self.root = master
        self.current_page = None
        self.width = 1920
        self.height = 1016

        self.pages = {
            "bypass_main": {
                "class": BypassMain,
                "bg": "images/bypass1.png",
                "width": self.width,
                "height": self.height,
            },
            "bypass_normal": {
                "class": BypassNormal,
                "bg": "images/bypass2.png",
                "width": self.width,
                "height": self.height,
            },
            "bypass_open": {
                "class": BypassOpen,
                "bg": "images/bypass3.png",
                "width": self.width,
                "height": self.height,
            },
            "bypass_on": {
                "class": BypassOn,
                "bg": "images/bypass4.png",
                "width": self.width,
                "height": self.height,
            },
            "bypass_off": {
                "class": BypassOff,
                "bg": "images/bypass5.png",
                "width": self.width,
                "height": self.height,
            }
        }
        self.root.title("APT OCP NIC 3.0 Network Test")
        # self.is_windows = platform.system() == 'Linux'
        self.show_page("bypass_main") 

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
