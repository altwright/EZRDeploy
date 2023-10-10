import tkinter as tk
from tkinter import ttk
from tab_content import ADTab, THTab, JCTab, create_grid, CompletedTaskTab, RunningTaskTab
from typing import List
from ioparsing import *
from appstate import appState, JobState, TaskState
from pypsexec.client import Client 
from datetime import datetime
from queue import Queue

class TabManager:
    def __init__(self, tabFrame, contentFrame):
        self.tabFrame = tabFrame
        self.contentFrame = contentFrame
        self.mainTabs = []
        self.deletableTabs = []

        tabData = ["Active Directory","Task History"]

        #created the main tabs and loads the data
        for i in range(len(tabData)):
            button = tk.Button(tabFrame, text=tabData[i], command=lambda c=tabData[i]: self.switch_to_required_page(c, None))
            self.mainTabs.append(button)
            button.grid(row=i, column=0, sticky="ew")
            self.tabFrame.grid_columnconfigure(i, weight=1)
        self.current_tab = ADTab(self.contentFrame, self.handle_ADTab)
        self.current_tab.create_page()
    
    #handles the data that the AD tab passes on
    def handle_ADTab(self, chosen_pc):
        self.current_tab.remove_page()
        self.current_tab = JCTab(self.contentFrame, self.handle_JCTab, chosen_pc)
        self.current_tab.create_page()
    
    #handles the data that the TH tab passes on 
    def handle_THTab(self, name):
        self.new_tab(name)
    
    def handle_RunningTab(self, switch_to_TH: bool):
        if switch_to_TH:
            #makes all tab buttons work again once Running tab has been left
            for main_tab_button in self.mainTabs:
                main_tab_button.config(state=tk.NORMAL)
            for deletable_tab_buttons in self.deletableTabs:
                deletable_tab_buttons["TAB_BUTTON"].config(state=tk.NORMAL)
                deletable_tab_buttons["DELETE_BUTTON"].config(state=tk.NORMAL)
            self.switch_to_required_page("Task History",None)

    def handle_JCTab(self, data):
        task = TaskState()
        task.name = data["NAME"]
        task.author = data["AUTHOR"]
        task.startDateTime = datetime.now()
        task.programStr = data["PROGRAM"]
        task.argsStr = data["ARGUMENTS"]
        task.localProgram = data["LOCALMACHINE"]
        task.localProgramSrcDir = data["LOCALSRC"]
        task.copyFiles = True if len(data["ADDFILES"]) > 0 else False
        task.copiedFilesList = data["ADDFILES"]
        task.remoteWorkingDir = data["WORKINGDIR"] if data["WORKINGDIR"] else None
        task.impersonateSysAdmin = data["SYSADMIN"]
        task.overwriteExe = data["OVERWRITE_EXE"]
        task.overwriteFiles = data["OVERWRITE_FILES"]
        task.cleanupExeAfterCopy = data["CLEANUP_EXE"]
        task.cleanupFilesAfterCopy = data["CLEANUP_FILES"]
        task.timeout = int(data["TIMEOUT"])

        for pcName in data["PCs"]:
            jobState = JobState()
            jobState.clientName = pcName
            jobState.client = Client(pcName)
            jobState.stdoutQ = Queue()
            jobState.job = Job(
                jobState.client,
                task.programStr,
                task.argsStr,
                jobState.stdoutQ,
                jobState.stdoutQ,
                copy_local_exe= task.localProgram,
                local_exe_src_dir=task.localProgramSrcDir,
                clean_copied_exe_after=task.cleanupExeAfterCopy,
                overwrite_remote_exe=task.overwriteExe,
                copy_local_files=task.copyFiles,
                src_files_list=task.copiedFilesList,
                overwrite_remote_files=task.overwriteFiles,
                clean_copied_files_after=task.cleanupFilesAfterCopy,
                use_system_account=task.impersonateSysAdmin,
                working_dir=task.remoteWorkingDir,
                timeout_seconds=task.timeout
            )

            task.jobList.append(jobState)

        appState.runningTasks.append(task)
        self.switch_to_required_page(None, task.name)

    #used to change tabs
    def switch_to_required_page(self, content_frame, task_name):
        targetTask: TaskState = None
        for runningTask in appState.runningTasks:
            if task_name == runningTask.name:
                targetTask = runningTask
                content_frame = "Running"
        for completedTask in appState.completedTasks:
            if task_name == completedTask.name:
                targetTask = completedTask
                content_frame = "Completed"
            
        self.current_tab.remove_page()
        if (content_frame == 'Active Directory'):
            self.current_tab = ADTab(self.contentFrame, self.handle_ADTab)
            self.current_tab.create_page()
        elif (content_frame == 'Task History'):
            self.current_tab = THTab(self.contentFrame, self.handle_THTab)
            self.current_tab.create_page()
        elif (content_frame == "Running"):
            self.current_tab = RunningTaskTab(self.contentFrame, targetTask, self.handle_RunningTab)

            #disables the other tab buttons so user cannot go anywhere else
            for main_tab_button in self.mainTabs:
                main_tab_button.config(state=tk.DISABLED)
            for deletable_tab_buttons in self.deletableTabs:
                deletable_tab_buttons["TAB_BUTTON"].config(state=tk.DISABLED)
                deletable_tab_buttons["DELETE_BUTTON"].config(state=tk.DISABLED)

        elif (content_frame == "Completed"):
            self.current_tab = CompletedTaskTab(self.contentFrame, targetTask)
            self.current_tab.create_page()

    #removes a tab and its frame
    def delete_tab_frame(self, taskName):
        for openTaskTab in self.deletableTabs:
            if taskName == openTaskTab["NAME"]:
                openTaskTab["FRAME"].destroy()
                self.deletableTabs.remove(openTaskTab)
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
    def new_tab(self, name):
        valid = True
        for data in self.deletableTabs:
            if name == data["NAME"]:
                valid = False
                break
        if valid:
            new_frame = tk.Frame(self.tabFrame, bg="blue")
            new_frame.grid(row=len(self.deletableTabs) + len(self.mainTabs), column=5, sticky="nsew", padx=3)

            inner_button = ttk.Button(new_frame, text=f"{name}", command=lambda name=name: self.switch_to_required_page(None, name))

            delete_button = ttk.Button(new_frame, text="X", width=2, command=lambda i=name: self.delete_tab_frame(i))
            delete_button.pack(side=tk.RIGHT)
            inner_button.pack(fill=tk.X)


            new_frame.delete_button = delete_button
            self.tabFrame.grid_columnconfigure(len(self.deletableTabs) + len(self.mainTabs), weight=1)
            data = {"NAME": name, "FRAME": new_frame, "TAB_BUTTON": inner_button, "DELETE_BUTTON": delete_button}
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
    TabManager(tabFrame, contentFrame)
    
    root.mainloop()
