import tkinter as tk
from tkinter import ttk
from tab_content import ADTab, THTab, JCTab, create_grid, resize_image, completedTab

class TabManager:
    def __init__(self, tabFrame, contentFrame):
        self.tabFrame = tabFrame
        self.contentFrame = contentFrame
        self.mainTabs = []
        self.deletableTabs = []

        self.tabData = [
            {"Name": "Active Directory", "content" : ADTab(self.contentFrame, self.handle_ADTab)},
            {"Name": "Task History", "content" : THTab(self.contentFrame, self.handle_THTab)},
            {"Name": "Job Creation", "content" : JCTab(self.contentFrame)},
        ]

        #created the main tabs and loads the data
        for i, info in enumerate(self.tabData):
            button = ttk.Button(self.tabFrame, text=info["Name"], command=lambda c=info["Name"]: self.show_content(c, None))
            self.mainTabs.append(button)
            button.grid(row=i, column=0, sticky="ew")
            self.tabFrame.grid_columnconfigure(i, weight=1)
    
    #handles the data that the AD tab passes on
    def handle_ADTab(self, chosen_pc):
        print(chosen_pc)
    
    #handles the data that the TH tab passes on 
    def handle_THTab(self, job_path):
        with open(job_path, 'r') as file:
            data = file.read().splitlines()
            name = data[0]
            self.new_tab(name, job_path)
            
    
    #used to change tabs
    def show_content(self, content_frame, data_list):
        for info in self.tabData:
            info["content"].remove_page()
        if (content_frame == 'Active Directory'):
            current_tab = ADTab(self.contentFrame, self.handle_ADTab)
        elif (content_frame == 'Task History'):
            current_tab = THTab(self.contentFrame, self.handle_THTab)
        elif (content_frame == "Job Creation"):
            current_tab = JCTab(self.contentFrame)
        else:
            current_tab = completedTab(self.contentFrame, data_list)
        current_tab.create_page()

    #removes a tab and its frame
    def delete_tab_frame(self, name):
        for data in self.deletableTabs:
            if name == data["NAME"]:
                data["FRAME"].destroy()
                self.deletableTabs.remove(data)
                self.rearrange_tab_frames()

    #fix tab frames to remove gaps when a tab is deleted
    def rearrange_tab_frames(self):
        for i, button in enumerate(self.mainTabs):
            button.grid(row=i, column=0, sticky="ew")
        for i, data in enumerate(self.deletableTabs):
            data["FRAME"].grid(row=len(self.mainTabs) + i, column=0, sticky="nsew", padx=3)

    #add new tab based on name (assuming name is the unique identifier)
    def new_tab(self, name, job_path):
        valid = True
        for data in self.deletableTabs:
            if name == data["NAME"]:
                valid = False
                break
        if valid:
            new_frame = tk.Frame(self.tabFrame, bg="blue")
            new_frame.grid(row=len(self.deletableTabs) + len(self.mainTabs), column=5, sticky="nsew", padx=3)

            inner_button = ttk.Button(new_frame, text=f"{name}", command=lambda path=job_path, name=name: self.show_content(name, path))

            delete_button = ttk.Button(new_frame, text="X", width=2, command=lambda i=name: self.delete_tab_frame(i))
            delete_button.pack(side=tk.RIGHT)
            inner_button.pack(fill=tk.X)


            new_frame.delete_button = delete_button
            self.tabFrame.grid_columnconfigure(len(self.deletableTabs) + len(self.mainTabs), weight=1)
            data = {"NAME": name, "FRAME": new_frame}
            self.deletableTabs.append(data)
            self.rearrange_tab_frames()
        else:
            print("tab is already open")
        

#main function where everything is called
def main():
    root = tk.Tk()
    root.minsize(1000, 800)
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
    contentFrame.grid(row=2, column=3, columnspan=20, rowspan=18, sticky="nsew")

    right_frame.grid_columnconfigure(3, weight=1)  # horizontal
    right_frame.grid_rowconfigure(2, weight=1)  # vertical

    tabFrame = tk.Frame(left_frame, bg="lightgray")
    tabFrame.grid(row=0, column=0, columnspan=20, sticky="nsew")
    tab_manager = TabManager(tabFrame, contentFrame)
    
    root.mainloop()

