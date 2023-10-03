import tkinter as tk
from tkinter import ttk
from tab_content import ADTab, THTab, JCTab, create_grid, completedTab
from typing import List
from ioparsing import *

class TabManager:
    def __init__(self, tabFrame, contentFrame):
        self.tabFrame = tabFrame
        self.contentFrame = contentFrame
        self.mainTabs = []
        self.deletableTabs = []

        tabData = ["Active Directory","Task History"]

        #created the main tabs and loads the data
        for i in range(len(tabData)):
            button = ttk.Button(tabFrame, text=tabData[i], command=lambda c=tabData[i]: self.show_content(c, None))
            self.mainTabs.append(button)
            button.grid(row=i, column=0, sticky="ew")
            self.tabFrame.grid_columnconfigure(i, weight=1)
        self.current_tab = ADTab(self.contentFrame, self.handle_ADTab)
    
    #handles the data that the AD tab passes on
    def handle_ADTab(self, chosen_pc):
        self.current_tab.remove_page()
        self.current_tab = JCTab(self.contentFrame, self.handle_JCTab, chosen_pc)
        self.current_tab.create_page()
    
    #handles the data that the TH tab passes on 
    def handle_THTab(self, job_path):
        with open(job_path, 'r') as file:
            data = file.read().splitlines()
            name = data[0]
            self.new_tab(name, job_path)

    def handle_JCTab(self, data):
        print("creating a job called...." , data["NAME"])
        print("with a program called....", data["PROGRAM"])
        print("With the arguments...", data["ARGUMENTS"])
        print("On the local machien....", data["LOCALMACHINE"])
        print("Run as system admin....", data["SYSADMIN"])
        print("With these additional Files....", data["ADDFILES"])
        print("Created by..." , data["AUTHOR"])
        print("With PCs:..." , data["PCs"])
        
        # replace with JCPage create_job_callback
        print()
    
    #used to change tabs
    def show_content(self, content_frame, data_list):
        self.current_tab.remove_page()
        if (content_frame == 'Active Directory'):
            self.current_tab = ADTab(self.contentFrame, self.handle_ADTab)
        elif (content_frame == 'Task History'):
            self.current_tab = THTab(self.contentFrame, self.handle_THTab)
        else:
            self.current_tab = completedTab(self.contentFrame, data_list)
        self.current_tab.create_page()


    #removes a tab and its frame
    def delete_tab_frame(self, name):
        for data in self.deletableTabs:
            if name == data["NAME"]:
                data["FRAME"].destroy()
                self.deletableTabs.remove(data)
                self.rearrange_tab_frames()
        self.current_tab.remove_page()
        self.current_tab = THTab(self.contentFrame, self.handle_THTab)
        self.current_tab.create_page()

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
def uiMain():
    root = tk.Tk()
    root.minsize(1000, 800)
    root.title("PAExec CyberForensic Tool")

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
    
    # definitions for lists storing AD clients and jobs, should go here, if not move elsewhere
    AD_clients: List = [] # type for client to be declared after List
    tasks: List[Task] = []
    task_pages: List[TaskPage] = []
    
    # these might need to be pulled into each page depending on whether they are used by the page
    
    root.mainloop()
