import tkinter as tk
from tab_content import ADTab, PJTab, CJTab

class TabApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Tab App")
        self.root.geometry("1000x600")
        
        self.tabs = tk.Frame(self.root)
        self.tabs.pack(side="top", fill="x")  # Place tab buttons at the top
        
        self.tab_buttons = []
        self.tab_frames = []
        
        tab_info = [
            {"title": "AD", "color": "lightblue", "content": ADTab},
            {"title": "PJ", "color": "lightgreen", "content": PJTab},
            {"title": "CJ", "color": "lightpink", "content": CJTab}
        ]
        
        for i, tab_data in enumerate(tab_info):
            tab_button = tk.Button(self.tabs, text=tab_data["title"], command=lambda i=i: self.show_tab(i))
            tab_button.pack(side="left")
            self.tab_buttons.append(tab_button)
                    
            tab_frame = tk.Frame(self.root, bg=tab_data["color"])
            self.tab_frames.append(tab_frame)
                    
            content_class = tab_data["content"]
            content_instance = content_class(tab_frame)
            content_instance.pack(fill="both", expand=True)
                
        self.show_tab(0)
        
    def show_tab(self, tab_index):
        for i in range(len(self.tab_frames)):
            if i == tab_index:
                self.tab_frames[i].pack(fill="both", expand=True)
                self.tab_buttons[i].config(relief="sunken")
            else:
                self.tab_frames[i].pack_forget()
                self.tab_buttons[i].config(relief="raised")

root = tk.Tk()
app = TabApp(root)
root.mainloop()
