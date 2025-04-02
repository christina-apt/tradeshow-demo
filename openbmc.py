import webbrowser

class OpenBMC:
    def __init__(self, master):
        self.master = master
        self.master.withdraw()
        self.open_browser()

    def open_browser(self):
        url = "http://root:Apt44200@200.200.200.102"
        webbrowser.open_new(url)