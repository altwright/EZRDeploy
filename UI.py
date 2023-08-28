import tkinter as tk
from tkinter import ttk
from tab_content import ADTab, PJTab, JCTab, create_grid, resize_image

class TabManager:
    def __init__(self, tabFrame, tabData):
        self.tabFrame = tabFrame
        self.tabData = tabData

        self.mainTabs = []
        self.deletableTabs = []

        #created the main tabs and loads the data
        for i, info in enumerate(self.tabData):
            button = ttk.Button(self.tabFrame, text=info["Name"], command=lambda c=info["content"]: self.show_content(c))
            self.mainTabs.append(button)
            button.grid(row=i, column=0, sticky="ew")
            self.tabFrame.grid_columnconfigure(i, weight=1)
    
    def show_content(self, content_frame):
        for info in self.tabData:
            info["content"].remove_page()
        content_frame.create_page()

    #removes a tab and its frame
    def delete_tab_frame(self, frame_number):
        self.deletableTabs[frame_number].destroy()
        del self.deletableTabs[frame_number]
        self.update_tab_frame_indices()
        self.rearrange_tab_frames()

    #updates the indices of the tabs in the arrays
    def update_tab_frame_indices(self):
        for i, frame in enumerate(self.deletableTabs):
            frame.delete_button.config(command=lambda i=i: self.delete_tab_frame(i))

    #fix tab frames to remove gaps when a tab is deleted
    def rearrange_tab_frames(self):
        for i, button in enumerate(self.mainTabs):
            button.grid(row=i, column=0, sticky="ew")
        for i, frame in enumerate(self.deletableTabs):
            frame.grid(row=len(self.mainTabs) + i, column=0, sticky="nsew", padx=3)

    #add new tab
    def new_tab(self):
        new_frame = tk.Frame(self.tabFrame, bg="blue")
        new_frame.grid(row=len(self.deletableTabs) + len(self.mainTabs), column=5, sticky="nsew", padx=3)

        inner_button = ttk.Button(new_frame, text=f"Task {len(self.deletableTabs) + 1}", command=None)

        delete_button = ttk.Button(new_frame, text="X", width=2, command=lambda: self.delete_tab_frame(len(self.deletableTabs)))
        delete_button.pack(side=tk.RIGHT)
        inner_button.pack(fill=tk.X)


        new_frame.delete_button = delete_button
        self.tabFrame.grid_columnconfigure(len(self.deletableTabs) + len(self.mainTabs), weight=1)
        self.deletableTabs.append(new_frame)
        self.update_tab_frame_indices()
        self.rearrange_tab_frames()

    def get_mainTabs(self):
        return self.mainTabs
    
    def get_deletableTabs(self):
        return self.deletableTabs

def starting_tab_data(contentFrame):
    #basic data of the main tabs
    tabData = [
        {"Name": "Active Directory", "content" : ADTab(contentFrame)},
        {"Name": "Past Jobs", "content" : PJTab(contentFrame)},
        {"Name": "Job Creation", "content" : JCTab(contentFrame)},
    ]
    return tabData

#main function where everything is called
def main():
    root = tk.Tk()
    root.minsize(600, 400)
    root.title("Digital Forensics tool")

    left_frame = tk.Frame(root)
    left_frame.grid(column=0, row=0, padx=10, pady=10)
    separator = ttk.Separator(root, orient="vertical")
    separator.grid(column=1, row=0, rowspan=3, sticky='nsew', padx=10)

    right_frame = tk.Frame(root)
    right_frame.grid(column=2, row=0, sticky="nsew")
    root.grid_columnconfigure(0, weight=1)
    root.grid_rowconfigure(0, weight=1)
    root.grid_columnconfigure(2, weight=18)

    contentFrame = tk.Frame(right_frame, bg="lightblue")

    # center frame
    contentFrame.grid(row=2, column=3, columnspan=20, rowspan=18, sticky="nsew")
    right_frame.grid_columnconfigure(3, weight=1)  # horizontal
    right_frame.grid_rowconfigure(2, weight=1)  # vertical

    tab_data = starting_tab_data(contentFrame)
    tabFrame = tk.Frame(left_frame, bg="lightgray")
    tabFrame.grid(row=0, column=0, columnspan=20, sticky="nsew")
    tab_manager = TabManager(tabFrame, tab_data)
    testing = ttk.Button(left_frame, text="Test", command=tab_manager.new_tab)
    testing.grid(row=1, column=0, sticky="ew", columnspan=2)
    
    root.mainloop()

