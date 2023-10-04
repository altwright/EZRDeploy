import os
import tkinter as tk
from queue import Queue
from tkinter import ttk
from tkinter import filedialog
from tkinter.filedialog import askdirectory as askDirectory
from console import ConsoleThread
from appstate import appState, TaskState, JobState
import socket

#used to create grid used in the frames
def create_grid(frame, rows, columns):
    for i in range(rows):
        frame.grid_rowconfigure(i, weight=1)
        for j in range(columns):
            frame.grid_columnconfigure(j, weight=1)

class ADTab(tk.Frame):
    def __init__(self, contentFrame, create_job_callback, master=None):
        super().__init__(master)
        self.frame = contentFrame
        self.create_job_callback = create_job_callback
        self.pc_buttons = []
        self.chosen_pc = []
        self.AllMachines = tk.BooleanVar()
        self.SearchGroup = tk.BooleanVar()
        self.SearchName = tk.BooleanVar()
        self.machine_list = self.gather_machines()
        create_grid(self.frame, 30, 30)
        #resize
        self.canvas = tk.Canvas(self.frame)
        self.canvas.grid(row=2, column=2, rowspan=26, columnspan=26, sticky="nsew")
        self.canvas.bind("<Configure>", self.update_padx)

    def update_padx(self, event=None):
        num_per_row = 5
        sub_frame_width = max(sub_frame.winfo_width() for sub_frame in self.frame.winfo_children())
        remaining_space = (self.canvas.winfo_width() - num_per_row * sub_frame_width) // (num_per_row + 1)
        padx = max(0, remaining_space // 2)

        for sub_frame in self.frame.winfo_children():
            sub_frame.grid_configure(padx=padx)
 
    #call back function used to send data back to tab_manager
    def call_create_job_callback(self):
        self.create_job_callback(self.chosen_pc)
    
    def gather_machines(self):
        #THIS FUNCTION GRABS DATA ABOUT THE MACHINE'S FROM THE ACTIVE DIRECTORY AND RETURNS IT AS AN ARRAY
        remoteComputers = appState.aDSession.find_computers_by_common_name("*", ['operatingSystem', 'operatingSystemVersion', 'dNSHostName'])
        remoteComputerInfos = []
        for computer in remoteComputers:
            if computer.name != appState.hostComputer:
                groups = appState.aDSession.find_groups_for_computer(computer)
                groupCommonNames = []
                for group in groups:
                    groupCommonNames.append(group.common_name)
                remoteComputerInfos.append({
                    "NAME": computer.name, 
                    "IP": socket.gethostbyname(computer.get('dNSHostName')), 
                    "GROUPS": groupCommonNames,
                    "OS": computer.get('operatingSystem'),
                    "OS_VERSION": computer.get('operatingSystemVersion')
                    })

        return remoteComputerInfos

    #Function called when Select all machines checkbox is called
    def select_all_machines(self):
        if self.AllMachines.get():
            #add all pc to list
            for i in range(len(self.machine_list)):
                self.add_pc_to_list(i, False)

        else:          
            #remove all pc from list
            for i in range(len(self.machine_list)):
                self.add_pc_to_list(i, False)
    


    def show_button(self):
        if len(self.chosen_pc) > 0:
            self.create_job.config(state=tk.NORMAL)
        else:
            self.create_job.config(state=tk.DISABLED)
    
    def select_group(self):
        if (self.SearchName.get()):
            self.SearchName.set("False")
        elif (self.SearchGroup.get()):
            self.search_input.config(state=tk.NORMAL)
            self.search_button.config(state=tk.NORMAL)
        elif (not self.SearchGroup.get()):
            self.search_input.config(state=tk.DISABLED)
            self.search_button.config(state=tk.DISABLED)
    
    def select_name(self):
        if (self.SearchGroup.get()):
            self.SearchGroup.set("False")
        elif (self.SearchName.get()):
            self.search_input.config(state=tk.NORMAL)
            self.search_button.config(state=tk.NORMAL)
        elif (not self.SearchName.get()):
            self.search_input.config(state=tk.DISABLED)
            self.search_button.config(state=tk.DISABLED)

    def create_page(self):
        self.count = 0
        title = tk.Label(self.frame, text = "Active Directory", font=("Arial Bold",20), bg="lightblue")
        title.grid(row=0, column=2, columnspan=2, sticky="nsew")

        top_frame = tk.LabelFrame(self.frame, font=("Arial Bold", 12))
        top_frame.grid(row=1, column=5, sticky="nsew", padx=10, pady=10)

        self.search_input = tk.Entry(top_frame, state=tk.DISABLED)
        self.search_input.insert(0, "Enter Search")
        self.search_input.bind("<FocusIn>", self.on_entry_focus_in)
        self.search_input.grid(row=1, rowspan=2, column=13, columnspan=2, sticky='ew')

        self.search_button = tk.Button(top_frame,text="Search", state=tk.DISABLED, command=lambda i=True: self.populate_pc_window(i))
        self.search_button.grid(row=1, rowspan=2, column=15, columnspan=2)

        self.display_all_mc = tk.Button(top_frame,text='Display all Machines', command=lambda i=False: self.populate_pc_window(i))
        self.display_all_mc.grid(row=1, rowspan=2, column=5 ,columnspan=2)
        
        self.display_by_group = ttk.Checkbutton(top_frame, text="Select by Group", variable=self.SearchGroup, onvalue=True, offvalue=False, command=self.select_group)
        self.display_by_group.grid(row=1, column=11, columnspan=1)
        self.display_by_name = ttk.Checkbutton(top_frame, text="Select by Name", variable=self.SearchName, onvalue=True, offvalue=False, command=self.select_name)
        self.display_by_name.grid(row=2, column=11, columnspan=1)

        self.select_all_button = ttk.Checkbutton(top_frame, text="Select All Machines", state=tk.DISABLED, variable=self.AllMachines, onvalue=True, offvalue=False, command=self.select_all_machines)
        self.select_all_button.grid(row=1,rowspan=2, column=25)

        self.create_job = ttk.Button(top_frame, text="Create New Job", state=tk.DISABLED, command=self.call_create_job_callback)
        self.create_job.grid(row=1, rowspan=2, column=28, columnspan=1)



    
    def populate_pc_window(self, search):
        if self.count == 1:
            for widget in self.canvas.winfo_children():
                widget.destroy()
            self.canvas.destroy()
        self.pc_buttons = []
        self.count = 1

        self.select_all_button.config(state=tk.NORMAL)
        # Create a Canvas widget for scrollable content
        self.canvas = tk.Canvas(self.frame)
        self.canvas.grid(row=3, column=2, rowspan=26, columnspan=26, sticky="nsew")

        #collect machine list from active directory
        if (search == False):
            pc_list = self.machine_list
        else:
            pc_list = self.gather_machines_search()
        num_rows = (len(pc_list)//5 + 1)

        # Create a Frame to contain the actual content
        content_frame = tk.Frame(self.canvas)
        self.canvas.create_window((0, 0), window=content_frame)

        # Define constants for layout
        num_per_row = 5
        spacing = 25  # Adjust as needed

        for i, data in enumerate(pc_list):
            
            # Calculate row and column based on index
            row = (i // num_per_row)*2
            col = i % num_per_row

            sub_frame = tk.Frame(content_frame)  # Create a sub-frame for each button-label pair
            create_grid(sub_frame, num_rows, 5)
            sub_frame.grid(row=row, column=col, padx=spacing, pady=spacing)
            

            pc_btn = tk.Button(sub_frame, text=data["NAME"], command=lambda i=i: self.add_pc_to_list(i, True))
            if data["NAME"] in self.chosen_pc:
                pc_btn.config(relief="sunken")

            pc_btn.grid(row=0, column=0)
            self.pc_buttons.append(pc_btn)
                    # Bind the toggle_button function to the button click event
            pc_btn.bind("<Button-1>", lambda event, i=i: self.add_pc_to_list(i, True))

            label = tk.Label(sub_frame, text="IP: "+ data["IP"])
            label.grid(row=1, column=0)

            # Calculate the width of sub_frame after it's been created
            sub_frame.update_idletasks()
            sub_frame_width = sub_frame.winfo_width()

            # Set padx to be half of the remaining space to center sub_frame
            remaining_space = (self.canvas.winfo_width() - num_per_row * sub_frame_width) // (num_per_row + 1)
            padx = max(0, remaining_space // 2)

            # Update padx for sub_frame
            sub_frame.grid_configure(padx=padx)
        


        # Add scrollbars
        y_scrollbar = tk.Scrollbar(self.frame, orient="vertical", command=self.canvas.yview)
        y_scrollbar.grid(row=2, column=29, rowspan=27, sticky="ns")
        self.canvas.configure(yscrollcommand=y_scrollbar.set)

        x_scrollbar = tk.Scrollbar(self.frame, orient="horizontal", command=self.canvas.xview)
        x_scrollbar.grid(row=29, column=2, columnspan=27, sticky="ew")
        self.canvas.configure(xscrollcommand=x_scrollbar.set) 

        # Update scrollable region
        content_frame.update_idletasks()
        self.canvas.config(scrollregion=self.canvas.bbox("all")) 

    def add_pc_to_list(self, button_index, individual):
        button = self.pc_buttons[button_index]
        button_text = button.cget("text")

        # Toggle between "sunken" and "raised" relief
        new_relief = "sunken" if button.cget("relief") == "raised" else "raised"

        if new_relief == "sunken" and individual:
            self.chosen_pc.append(button_text)
            button.config(state=tk.DISABLED)  # Disable the button when it's in the "sunken" state
        elif new_relief == "raised" and individual:
                if button_text in self.chosen_pc:
                    self.chosen_pc.remove(button_text)
                    self.AllMachines.set("False")
                    button.config(state=tk.NORMAL)  # Enable the button when it's in the "raised" state


        elif self.AllMachines.get() == True and not individual:
            if button_text not in self.chosen_pc:
                self.chosen_pc.append(button_text)

        elif self.AllMachines.get() == False and not individual:
            if button_text in self.chosen_pc:
                self.chosen_pc.remove(button_text)

        self.show_button()
        button.config(relief=new_relief)

    def gather_machines_search(self):
        data = self.machine_list
        filtered_data = []
        search_filter = self.search_input.get()

        if self.SearchGroup.get():
            for content in data:
                if search_filter.lower() in content["GROUP"].lower():
                    filtered_data.append(content)
        
        if self.SearchName.get():
            for content in data:
                if search_filter.lower() in content["NAME"].lower():
                    filtered_data.append(content)
        return filtered_data

    def on_entry_focus_in(self, event):
        if event.widget.get() == "Enter Search":
            event.widget.delete(0, "end")

    def remove_page(self):
        for widget in self.frame.winfo_children():
            widget.destroy()

class THTab(tk.Frame):
    def __init__(self, contentFrame, create_job_callback, master=None):
        super().__init__(master)
        self.frame = contentFrame
        self.create_job_callback = create_job_callback
        create_grid(self.frame, 30, 30)

        self.canvas = tk.Canvas(self.frame)
        self.canvas.grid(row=2, column=2, rowspan=26, columnspan=26, sticky="nsew")
        self.canvas.bind("<Configure>", self.update_padx)

        self.past_jobs = []

    def update_padx(self, event=None):
        num_per_row = 6
        sub_frame_width = max(sub_frame.winfo_width() for sub_frame in self.frame.winfo_children())
        remaining_space = (self.canvas.winfo_width() - num_per_row * sub_frame_width) // (num_per_row + 1)
        padx = max(0, remaining_space // 2)

        for sub_frame in self.frame.winfo_children():
            sub_frame.grid_configure(padx=padx)

    #creats a call back function to pass data back to tab_manager
    def call_create_job_callback(self, name):
        self.create_job_callback(name)
    
    #shows whats in the search bar
    def display_search(self):
        search_text = self.search_bar.get()
        print(search_text)

    def create_page(self):
        title = tk.Label(self.frame, text = "Task History", font=("Arial Bold",20), bg="lightblue")
        title.grid(row=0, column=2, columnspan=2, sticky="w")

        self.search_bar = tk.Entry(self.frame)
        self.search_bar.insert(0, "Enter search")
        self.search_bar.grid(row=1, column=2, columnspan=4, sticky="ew")

        search_bar_btn = ttk.Button(self.frame, text="Search", command=self.display_search)
        search_bar_btn.grid(row=1, column=7, columnspan=2, sticky="ew")

        canvas = tk.Canvas(self.frame)
        canvas.grid(row=2, column=2, rowspan=26, columnspan=26, sticky="nsew")

        content_frame = tk.Frame(canvas)
        canvas.create_window((0, 0), window=content_frame)

        self.gather_task_details()
        self.populate_scrollwindow(content_frame)

        #for scroll bars
        y_scrollbar = tk.Scrollbar(self.frame, orient="vertical", command=canvas.yview)
        y_scrollbar.grid(row=2, column=29, rowspan=26, sticky="ns")
        canvas.configure(yscrollcommand=y_scrollbar.set)

        x_scrollbar = tk.Scrollbar(self.frame, orient="horizontal", command=canvas.xview)
        x_scrollbar.grid(row=29, column=2, columnspan=26, sticky="ew")
        canvas.configure(xscrollcommand=x_scrollbar.set)

        self.canvas.config(scrollregion=self.canvas.bbox("all"))

        
        content_frame.update_idletasks()
        canvas.config(scrollregion=canvas.bbox("all")) 
    
    def gather_task_details(self):
        self.past_jobs = []
        for data in appState.runningTasks:
            data_elements = { 
                "NAME" : data.name,
                "NUM_COMP" : len(data.jobList),
                "DATE" : data.startDateTime,
                "PROGRAM" : data.programStr,
                "STATUS" : "Running"
            }
            self.past_jobs.append(data_elements)

        for data in appState.completedTasks:
            data_elements = { 
                "NAME" : data.name,
                "NUM_COMP" : len(data.jobList),
                "DATE" : data.startDateTime,
                "PROGRAM" : data.programStr,
                "STATUS" : "Completed"
            }
            self.past_jobs.append(data_elements)

    def populate_scrollwindow(self, canvas):
        data_frame = tk.Frame(canvas)
        data_frame.grid(row=0, column=0, sticky="nsew")
        
        for i in range(6):
            data_frame.grid_columnconfigure(i, weight=1)
        data_frame.grid(row=0, column=0, sticky="nsew")
        for i, data in enumerate(self.past_jobs):
            data_elements = [
                f"Name: {data['NAME']}",
                f"Number of Machines: {data['NUM_COMP']}",
                f"Date Started: {data['DATE']}",
                f"Program: {data['PROGRAM']}",
                f"Status: {data['STATUS']}"
            ]

            # create LabelFrame for job
            job_frame = tk.LabelFrame(data_frame, text=f"Job {i + 1}", font=("Arial Bold", 12))
            job_frame.grid(row=i+1, column=0, sticky="nsew", padx=10, pady=10)

            for k, obj in enumerate(data_elements):
                info = tk.Label(job_frame, text=obj, font=("Arial Bold", 12))
                info.grid(row=0, column=k, sticky="w")
                job_frame.grid_columnconfigure(k, weight=1)
            

            button = tk.Button(job_frame, text=f"Inspect {data['NAME']}", command=lambda name=data["NAME"]: self.call_create_job_callback(name))
            button.grid(row=0, column=5, sticky="e")
            

        data_frame.grid_rowconfigure(0, weight=1)
        data_frame.grid_columnconfigure(0, weight=1)
        

        y_scrollbar = tk.Scrollbar(self.frame, orient="vertical", command=self.canvas.yview)
        y_scrollbar.grid(row=2, column=29, rowspan=26, sticky="ns")
        self.canvas.configure(yscrollcommand=y_scrollbar.set)

        x_scrollbar = tk.Scrollbar(self.frame, orient="horizontal", command=self.canvas.xview)
        x_scrollbar.grid(row=29, column=2, columnspan=26, sticky="ew")
        self.canvas.configure(xscrollcommand=x_scrollbar.set)
  
        data_frame.update_idletasks()
        self.canvas.config(scrollregion=self.canvas.bbox("all"))


    def remove_page(self):
        for widget in self.frame.winfo_children():
            widget.destroy()


class JCTab(tk.Frame):
    def __init__(self, contentFrame, create_job_callback, chosen_pc, master=None):
        super().__init__(master)
        self.frame = contentFrame
        self.create_job_callback = create_job_callback
        self.chosen_pc = chosen_pc
        self.validPath = False
        self.validName = False
        self.validTimeout = False
        self.validFiles = True
        self.additionalFileList = []
        create_grid(self.frame, 30, 30)

    def create_page(self):
        main_title = tk.Label(self.frame, text = "Job Configuration", font=("Arial Bold",20), bg="lightblue")
        main_title.grid(row=0, column=2, columnspan=2, sticky="w")


        #this section is for the author's name input 
        authorFame = tk.Frame(self.frame, bg="lightblue")
        authorFame.grid(row=1, column=2, columnspan=19, sticky="ew")

        author_title = tk.Label(authorFame, text="Author Name:", font=("Arial Bold",12), bg="lightblue")
        author_title.pack(side=tk.LEFT)

        self.author_input = tk.Entry(authorFame)
        self.author_input.insert(0, "Enter Author's Name")
        self.author_input.bind("<FocusIn>", self.on_entry_focus_in)
        self.author_input.pack(fill=tk.BOTH)


        #this section is for the name input and calls functions to make sure its valid
        nameFame = tk.Frame(self.frame, bg="lightblue")
        nameFame.grid(row=2, column=2, columnspan=19, sticky="ew")

        name_title = tk.Label(nameFame, text="Task Name:", font=("Arial Bold",12), bg="lightblue")
        name_title.pack(side=tk.LEFT)

        self.name_input = tk.Entry(nameFame)
        self.name_input.insert(0, "Enter Job Title")
        self.name_input.bind("<FocusIn>", self.on_entry_focus_in)
        self.name_input.pack(fill=tk.BOTH)
        reg1 = self.name_input.register(self.validate_name)
        self.name_input.config(validate ="key", validatecommand =(reg1, '%P'))

        self.valid_name = tk.Label(self.frame, text="Invalid Task Name", font=("Arial Bold",12), fg="red", bg='lightblue')
        self.valid_name.grid(row=3, column=2, columnspan=19)

        #program absoulute path title
        exeFame = tk.Frame(self.frame, bg="lightblue")
        exeFame.grid(row=4, column=2, columnspan=19, sticky="ew")

        program_title = tk.Label(exeFame, text="Executable:", font=("Arial Bold",12), bg="lightblue")
        program_title.pack(side=tk.LEFT)

        #this section is for the program path input and calls functions to make sure its valid
        self.program_input = tk.Entry(exeFame)
        self.program_input.insert(0, "Enter Executable Program")
        self.program_input.bind("<FocusIn>", self.on_entry_focus_in)
        self.program_input.pack(fill=tk.BOTH)
        reg2 = self.frame.register(self.check_program)
        self.program_input.config(validate ="key", validatecommand =(reg2, '%P'))

        ##
        #section is for executabe arguments
        ##
        argFame = tk.Frame(self.frame, bg="lightblue")
        argFame.grid(row=5, column=2, columnspan=19, sticky="ew")

        arg_title = tk.Label(argFame, text="Arguments:", font=("Arial Bold",12), bg="lightblue")
        arg_title.pack(side=tk.LEFT)

        self.arg_input = tk.Entry(argFame)
        self.arg_input.insert(0, "Arguments")
        self.arg_input.bind("<FocusIn>", self.on_entry_focus_in)
        self.arg_input.pack(fill=tk.BOTH)


        #check button for making sure if program in on local machine or remote
        self.localMachine = tk.BooleanVar()
        #initially set to false
        self.localMachine.set("False")
        localMachine_option_button = ttk.Checkbutton(self.frame, text="Select Program on Local Machine", variable=self.localMachine, onvalue=True, offvalue=False, command=self.local_machine_option)
        localMachine_option_button.grid(row=6, column=2, columnspan=8)

        #button used to open a file explorer
        self.button_explore = ttk.Button(self.frame, text = "Browse Files", state=tk.DISABLED, command=lambda i=1: self.dir_file_explorer(i))
        self.button_explore.grid(row=6, column=10, columnspan=8)

        ##
        #section is for local exe source directory
        ##

        exe_dir_title = tk.Label(self.frame, text="Local Executable Source Directory", font=("Arial Bold",12), bg="lightblue")
        exe_dir_title.grid(row=7, column=2, columnspan=19)

        self.exe_dir_input = tk.Entry(self.frame)
        self.exe_dir_input.insert(0, "Enter Directory")
        self.exe_dir_input.bind("<FocusIn>", self.on_entry_focus_in)
        self.exe_dir_input.config(state=tk.DISABLED)
        self.exe_dir_input.grid(row=8, column=2, columnspan=19, sticky="ew")
        reg4 = self.frame.register(self.check_path)
        self.exe_dir_input.config(validate ="key", validatecommand =(reg4, '%P'))

        #used to display to user if path for executable entered is valid
        self.valid_path = tk.Label(self.frame, font=("Arial Bold",12), fg="lightgreen", bg='lightblue')
        self.valid_path.grid(row=9, column=2, columnspan=19)


        ##
        ##this section is for the working directory part
        ##
        working_dir_title = tk.Label(self.frame, text="Local Machine's Working Directory", font=("Arial Bold",12), bg="lightblue")
        working_dir_title.grid(row=10, column=2, columnspan=19)

        self.working_dir_input = tk.Entry(self.frame)
        self.working_dir_input.insert(0, "Enter Working Directory")
        self.working_dir_input.bind("<FocusIn>", self.on_entry_focus_in)
        self.working_dir_input.grid(row=11, column=2, columnspan=19, sticky="ew")


        #this section is for the timeout 
        timeoutFame = tk.Frame(self.frame, bg="lightblue")
        timeoutFame.grid(row=12, column=2, columnspan=19, sticky="ew")

        timeout_title = tk.Label(timeoutFame, text="Timeout Number:", font=("Arial Bold",12), bg="lightblue")
        timeout_title.pack(side=tk.LEFT)

        self.timeout_input = tk.Entry(timeoutFame)
        self.timeout_input.insert(0, "Number")
        self.timeout_input.bind("<FocusIn>", self.on_entry_focus_in)
        self.timeout_input.pack(fill=tk.BOTH)
        reg3 = self.frame.register(self.check_timeout)
        self.timeout_input.config(validate ="key", validatecommand =(reg3, '%P'))

        self.valid_timeout = tk.Label(self.frame, text="Invalid Timeout Number", font=("Arial Bold",12), fg="red", bg='lightblue')
        self.valid_timeout.grid(row=13, column=2, columnspan=19)
        
        #check button for running program as system admin
        self.sysAdmin = tk.BooleanVar()
        #initially set to false
        self.sysAdmin.set("False")
        sysAdmin_button = ttk.Checkbutton(self.frame, text="Run Program as System Admin", variable=self.sysAdmin, onvalue=True, offvalue=False)
        sysAdmin_button.grid(row=14, column=2, columnspan=19)

        self.overwriteExe = tk.BooleanVar()
        self.overwriteExe.set("False")
        self.overwriteExe_option_button = ttk.Checkbutton(self.frame, text="Overwrite Remote Executable",state=tk.DISABLED, variable=self.overwriteExe, onvalue=True, offvalue=False)
        self.overwriteExe_option_button.grid(row=16, column=2, columnspan=9)

        self.overwriteFiles = tk.BooleanVar()
        self.overwriteFiles.set("False")
        self.overwriteFiles_option_button = ttk.Checkbutton(self.frame, text="Overwrite Remote Files",state=tk.DISABLED, variable=self.overwriteFiles, onvalue=True, offvalue=False)
        self.overwriteFiles_option_button.grid(row=16, column=11, columnspan=9)

        self.cleanupExe = tk.BooleanVar()
        self.cleanupExe.set("False")
        self.cleanupExe_option_button = ttk.Checkbutton(self.frame, text="Cleanup Copied Executable",state=tk.DISABLED, variable=self.cleanupExe, onvalue=True, offvalue=False)
        self.cleanupExe_option_button.grid(row=17, column=2, columnspan=9)

        self.cleanupFiles = tk.BooleanVar()
        self.cleanupFiles.set("False")
        self.cleanupFiles_option_button = ttk.Checkbutton(self.frame, text="Cleanup Copied Files",state=tk.DISABLED, variable=self.cleanupFiles, onvalue=True, offvalue=False)
        self.cleanupFiles_option_button.grid(row=17, column=11, columnspan=9)

        ##
        #adding additional files to be sent over
        ##

        #used to check if user wants to send over additional files
        self.additionalFile = tk.BooleanVar()
        self.additionalFile.set("False")
        additionalFile_option_button = ttk.Checkbutton(self.frame, text="Send Additional Files", variable=self.additionalFile, onvalue=True, offvalue=False, command=self.additional_file_option)
        additionalFile_option_button.grid(row=19, column=2, columnspan=19)

        #file absoulute path title
        file_title = tk.Label(self.frame, text="Files's Absolute Path:", font=("Arial Bold",12), bg="lightblue")
        file_title.grid(row=21, column=2, columnspan=19)

        #Used to all user to enter additional files
        self.additionalFile_input = tk.Entry(self.frame)
        self.additionalFile_input.insert(0, "Enter Additional File Aboslute Path")
        self.additionalFile_input.bind("<FocusIn>", self.on_entry_focus_in)
        self.additionalFile_input.config(state=tk.DISABLED)
        self.additionalFile_input.grid(row=22, column=2, columnspan=19, sticky="ew")
        reg3 = self.frame.register(self.validate_file_path)
        self.additionalFile_input.config(validate ="key", validatecommand =(reg3, '%P'))

        self.valid_additionalFile_path = tk.Label(self.frame, font=("Arial Bold",12), fg="green", bg='lightblue')
        self.valid_additionalFile_path.grid(row=23, column=2, columnspan=19)

        #button used to add file to list of other additional files
        self.additionalFile_Button = ttk.Button(self.frame, text="Add File", state=tk.DISABLED, command=self.add_additional_file)
        self.additionalFile_Button.grid(row=24, column=2, columnspan=19)

        #button used to open a file explorer for additional files
        self.additionalFiles_button_explore = ttk.Button(self.frame, text = "Browse Files", state=tk.DISABLED, command=lambda i=2: self.file_explorer(i))
        self.additionalFiles_button_explore.grid(row=25, column=2, columnspan=19)

        #button used to view all additional files added so far
        self.additionalFile_view_Button = ttk.Button(self.frame, text="View All Additional Files Chosen", state=tk.DISABLED, command=self.create_file_window)
        self.additionalFile_view_Button.grid(row=26, column=2, columnspan=19)

        self.valid_additionalFiles = tk.Label(self.frame, font=("Arial Bold",12), fg="green", bg='lightblue')
        self.valid_additionalFiles.grid(row=27, column=2, columnspan=19)


        #create job button
        self.create_job = ttk.Button(self.frame, text="Create New Job", state=tk.DISABLED, command=self.call_create_job_callback)
        self.create_job.grid(row=28, column=2, columnspan=19)


        #past job config side of page
        side_title = tk.Label(self.frame, text = "Past Job Configuration", font=("Arial Bold",16), bg="lightblue")
        side_title.grid(row=0, column=23, columnspan=2, sticky="w")

        self.search_bar = tk.Entry(self.frame)
        self.search_bar.insert(0, "Enter search")
        self.search_bar.bind("<FocusIn>", self.on_entry_focus_in)
        self.search_bar.grid(row=1, column=23, columnspan=2, sticky="ew")

        self.canvas = tk.Canvas(self.frame)
        self.canvas.grid(row=2, column=23, rowspan=14, columnspan=6, sticky="nsew")
        self.set_mousewheel(self.canvas, lambda e: self.canvas.config(text=e.delta), 1)

        self.content_frame = tk.Frame(self.canvas)
        self.canvas.create_window((0, 0), window=self.content_frame)

        self.search_directory()
        self.populate_scrollwindow(self.content_frame, '')

        y_scrollbar = tk.Scrollbar(self.frame, orient="vertical", command=self.canvas.yview)
        y_scrollbar.grid(row=2, column=29, rowspan=14, sticky="ns")
        self.canvas.configure(yscrollcommand=y_scrollbar.set)

        #search button and view all buttons are made down here as self.content_frame needs to be created for the commands these buttons lead to to be able to work
        search_bar_btn = ttk.Button(self.frame, text="Search", command=lambda: self.collect_search_data(False))
        search_bar_btn.grid(row=1, column=25, columnspan=2, sticky="ew")

        view_all_btn = ttk.Button(self.frame, text="view All", command=lambda: self.collect_search_data(True))
        view_all_btn.grid(row=1, column=27, columnspan=2, sticky="ew")


        #displaty Chosen PC's
        chosen_pc_title = tk.Label(self.frame, text = "Chosen Machines", font=("Arial Bold",16), bg="lightblue")
        chosen_pc_title.grid(row=16, column=23, columnspan=2, sticky="w")

        self.canvas2 = tk.Canvas(self.frame)
        self.canvas2.grid(row=17, column=23, rowspan=12, columnspan=6, sticky="nsew")
        self.set_mousewheel(self.canvas2, lambda e: self.canvas2.config(text=e.delta), 2)

        content_frame2 = tk.Frame(self.canvas2)
        self.canvas2.create_window((0, 0), window=content_frame2)
        
        self.populate_chosenMachine(content_frame2)

        y_scrollbar2 = tk.Scrollbar(self.frame, orient="vertical", command=self.canvas2.yview)
        y_scrollbar2.grid(row=17, column=29, rowspan=12, sticky="ns")
        self.canvas2.configure(yscrollcommand=y_scrollbar2.set)

        content_frame2.update_idletasks()
        self.canvas.config(scrollregion=self.canvas.bbox("all")) 
        self.canvas2.config(scrollregion=self.canvas2.bbox("all")) 

    #this function is used to allow the user to hover their mouse over the canvas widget and then scroll up and down the canvas using their mouse wheel
    def set_mousewheel(self, widget, command, canvas):
        #Activate / deactivate mousewheel scrolling when 
        #cursor is over / not over the widget respectively.
        if canvas == 2:
            widget.bind("<Enter>", lambda _: widget.bind_all('<MouseWheel>', self._on_mousewheel_canvas2))
            widget.bind("<Leave>", lambda _: widget.unbind_all('<MouseWheel>'))
        elif canvas == 1:
            widget.bind("<Enter>", lambda _: widget.bind_all('<MouseWheel>', self._on_mousewheel_canvas1))
            widget.bind("<Leave>", lambda _: widget.unbind_all('<MouseWheel>'))
    
    #the actual function used to scroll, has a bounds checks so can't scroll above content
    def _on_mousewheel_canvas2(self, event):
        content_height = self.canvas2.bbox("all")[3] - self.canvas2.bbox("all")[1]
        visible_height = self.canvas2.winfo_height()
        if content_height > visible_height:
            self.canvas2.yview_scroll(int(-1 * (event.delta / 120)), "units")
        else:
            self.canvas2.yview_moveto(0)
    
    def _on_mousewheel_canvas1(self, event):
        content_height = self.canvas.bbox("all")[3] - self.canvas.bbox("all")[1]
        visible_height = self.canvas.winfo_height()
        if content_height > visible_height:
            self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        else:
            self.canvas.yview_moveto(0)

    #used to add an additional file to a list of other additional files
    def add_additional_file(self):
        if self.additionalFile_input.get() not in self.additionalFileList:
            self.additionalFileList.append(self.additionalFile_input.get())
            self.additionalFile_input.delete(0,"end")
        self.validate_files()
        self.show_button()

    def check_program(self, input):
        if input != '':
            path = self.exe_dir_input.get() + "/" + input
            path.replace('\\','/')
            self.validate_path(path)
        else:
            self.validate_path(input)
        return True
    
    def check_path(self, input):
        if input != '':
            path = input + "/" + self.program_input.get()
            path.replace('\\','/')
            self.validate_path(path)
        else:
            self.validate_path(input)
        return True

    def check_timeout(self, input):
        if input.isnumeric():
            self.valid_timeout['text'] = 'Valid Path'
            self.valid_timeout.config(fg="green")
            self.validTimeout = True
        else:
            self.valid_timeout['text'] = 'Invalid Timeout Number'
            self.valid_timeout.config(fg="red")
            self.validTimeout = False
        self.validate_files()
        self.show_button()
        return True

    #used to change state of button_explore
    def local_machine_option(self):
        if self.localMachine.get():
            self.cleanupFiles_option_button.config(state=tk.NORMAL)
            self.cleanupExe_option_button.config(state=tk.NORMAL)
            self.overwriteFiles_option_button.config(state=tk.NORMAL)
            self.overwriteExe_option_button.config(state=tk.NORMAL)
            self.button_explore.config(state=tk.NORMAL)
            self.exe_dir_input.config(state=tk.NORMAL)
            path = self.exe_dir_input.get() + "/" + self.program_input.get()
            path.replace('\\','/')
            self.validate_path(path)
        else:
            self.cleanupFiles.set("False")
            self.cleanupFiles_option_button.config(state=tk.DISABLED)
            self.cleanupExe.set("False")
            self.cleanupExe_option_button.config(state=tk.DISABLED)
            self.overwriteFiles.set("False")
            self.overwriteFiles_option_button.config(state=tk.DISABLED)
            self.overwriteExe.set("False")
            self.overwriteExe_option_button.config(state=tk.DISABLED)
            self.button_explore.config(state=tk.DISABLED)
            self.exe_dir_input.delete(0,tk.END)
            self.exe_dir_input.insert(0,"Enter Directory")
            self.exe_dir_input.config(state=tk.DISABLED)
            self.valid_path['text'] = ''
            self.validPath = True
            self.validate_path(self.program_input.get())
        self.show_button() 
    
    #used to change the state of buttons and entry widget involved in sending additional files
    def additional_file_option(self):
        if self.additionalFile.get():
            self.additionalFile_input.config(state=tk.NORMAL)
            self.additionalFiles_button_explore.config(state=tk.NORMAL)
            self.additionalFile_view_Button.config(state=tk.NORMAL)
            self.validate_file_path(self.additionalFile_input.get())
            self.validate_files()
        else:
            self.additionalFile_input.config(state=tk.DISABLED)
            self.additionalFile_view_Button.config(state=tk.DISABLED)
            self.additionalFiles_button_explore.config(state=tk.DISABLED)
            self.additionalFile_Button.config(state=tk.DISABLED)
            self.valid_additionalFile_path['text'] = ''
            self.valid_additionalFiles['text'] = ''
            self.validFiles = True
        self.show_button()           

    def collect_search_data(self, all):
        if all:
            self.find_search('')
        else:
            self.find_search(self.search_bar.get())
        
    #Function is just a stub that displays what was typed in the search bar
    def find_search(self, search_text):
        self.search_bar.delete(0, "end")
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        self.populate_scrollwindow(self.content_frame, search_text)

    #serach the task history directory for details on past jobs
    def search_directory(self):
        self.past_jobs = []
        for filename in os.listdir("./task_history_files/"):
            if filename.endswith(".txt"):
                file_path = os.path.join("./task_history_files/", filename)
                self.process_text_file("task_history_files/"+filename)

    #collects data from the files (assuming first 3 lines hold all neccessary info)
    def process_text_file(self, filename):
        absolute_path = os.path.abspath(filename)
        with open(absolute_path, 'r') as file:
            data = file.read().splitlines()
            program = data[2]
            job = {"NAME": data[0], "DATE":data[4], "PATH": program}
            self.past_jobs.append(job)

    #function fills in the past job configuration scrollwindow with data and buttons. saerched is a string of what the user is searching for
    #if searched is blank, searching for nothing
    def populate_scrollwindow(self, frame, searched):
        for i, data in enumerate(self.past_jobs):
            concatenated_data = f"{data['NAME']}....{data['DATE']}"
            if searched == "" or (searched.lower() in concatenated_data.lower()):
                data_frame = tk.Frame(frame)
                data_frame.grid(row=i+1, column=0, sticky="nsew")

                info = tk.Label(data_frame, text=concatenated_data, font=("Arial Bold",12))
                info.grid(row=i+1, column=0, sticky="w", pady=10)

                button = tk.Button(data_frame, text=f"Load Configuration", command= lambda path= data['PATH']: self.load_past_data(path, 1))
                button.grid(row=i+1, column=1, sticky="e")


    
    def populate_chosenMachine(self, frame):
        data_frame = tk.Frame(frame)
        data_frame.grid(row=0, column=0, sticky="nsew")

        data_label = tk.Label(data_frame, text=str("-"*50), bg="lightblue")
        data_label.grid(row=0, column=0, sticky="nsew")
        for i in range(len(self.chosen_pc)):
            data_frame = tk.Frame(frame)
            data_frame.grid(row=i+1, column=0, sticky="nsew")

            info = tk.Label(data_frame, text=self.chosen_pc[i], font=("Arial Bold",12))
            info.grid(row=i+1, column=0, sticky="w", pady=10)

    
    #function loads the path of a past job config into the path entry widget for the upcomming job
    def load_past_data(self, path, section):
        if section == 1:
            self.exe_dir_input.delete(0,"end")  
            self.exe_dir_input.insert(0, path)
        else:
            self.additionalFile_input.delete(0,"end")  
            self.additionalFile_input.insert(0, path)

    #function validates if input in path's entry widget is valid
    def validate_path(self, input):
        if self.localMachine.get():
            if (os.path.exists(input)):
                self.valid_path['text'] = 'Valid Path'
                self.valid_path.config(fg="green")
                self.validPath = True
            else:
                self.valid_path['text'] = 'Invalid Path'
                self.valid_path.config(fg="red")
                self.validPath = False
        elif input != '':
            #assuming the absolute path they entered in is correct(program is loacted on remote machine, so no way of checking until we send a message to the remote machine)
            self.validPath = True
            self.valid_path['text'] = ''
        else:
            self.validPath = False
        self.validate_files()
        self.show_button()

    #function validates if input in name's entry widget is valid
    def validate_name(self, input):
        valid = True
        for data in self.past_jobs:
            if input == data["NAME"] or input == data["NAME"].replace(' ', '_') or input == '' or input == "Enter Job Title":
                valid = False

        if valid:
            self.valid_name['text'] = 'Valid Name'
            self.valid_name.config(fg="green")
            self.validName = True
        else:
            self.valid_name['text'] = 'Invalid Name'
            self.valid_name.config(fg="red")
            self.validName = False
        self.validate_files()
        self.show_button()
        return True
    
    def validate_file_path(self, input):
        if self.additionalFile.get():
            if os.path.exists(input):
                self.valid_additionalFile_path['text'] = 'Valid Path'
                self.valid_additionalFile_path.config(fg="green")
                self.additionalFile_Button.config(state=tk.NORMAL)
            else:
                self.valid_additionalFile_path['text'] = 'Invalid Path'
                self.valid_additionalFile_path.config(fg="red")
                self.additionalFile_Button.config(state=tk.DISABLED)
        else:
            self.valid_additionalFile_path['text'] = ''
        return True
    
    def validate_files(self):
        valid = True
        for data in self.additionalFileList:
            if not os.path.exists(data):
                valid = False
                
        if valid:
            self.valid_additionalFiles['text'] = 'Valid File Paths'
            self.valid_additionalFiles.config(fg="green")
            self.validFiles = True
        else:
            self.valid_additionalFiles['text'] = 'Invalid File Paths'
            self.valid_additionalFiles.config(fg="red")
            self.validFiles = False


    
    #this function is used to see if the create job button can be clickable/shown to user
    def show_button(self):
        if self.validName and self.validPath and not self.additionalFile.get() and self.validTimeout:
            self.create_job.config(state=tk.NORMAL)
        elif self.validName and self.validPath and self.additionalFile.get() and self.validFiles and self.validTimeout:
            self.create_job.config(state=tk.NORMAL)
        else:
            self.create_job.config(state=tk.DISABLED)
    
    #function used to send data back to tab_manager
    def call_create_job_callback(self):
        self.validate_files()
        if (self.validName and self.validPath and self.validTimeout and not self.additionalFile.get()) \
        or (self.validName and self.validPath and self.validTimeout and self.additionalFile.get() and self.validFiles):
            arguments = self.arg_input.get()
            workingDir = self.working_dir_input.get()
            localsrc = self.exe_dir_input.get()
            author = self.author_input.get()
            if arguments == "Arguments:":
                arguments = ''
            if author == 'Enter Author\'s Name':
                author = ''
            if workingDir == "Enter Working Directory":
                workingDir = ''
            if localsrc == "Enter Directory":
                localsrc = ''
            results = {"AUTHOR" : author,
                    "NAME": self.name_input.get(), 
                    "PROGRAM": self.program_input.get(),
                    "LOCALMACHINE": self.localMachine.get(),
                    "LOCALSRC": localsrc,
                    "WORKINGDIR": workingDir,
                    "ARGUMENTS": arguments,
                    "SYSADMIN": self.sysAdmin.get(), 
                    "OVERWRITE_FILES": self.overwriteFiles.get(),
                    "OVERWRITE_EXE": self.overwriteExe.get(), 
                    "TIMEOUT": self.timeout_input.get(),
                    "CLEANUP_EXE": self.cleanupExe.get(),
                    "CLEANUP_FILES": self.cleanupFiles.get(),
                    "ADDFILES": [],
                    "PCs": self.chosen_pc}
            if self.additionalFile.get():
                results["ADDFILES"] = self.additionalFileList
            self.create_job_callback(results)

    #function used to create a file explorer    
    def file_explorer(self, section):
        filename = filedialog.askopenfilename(initialdir = "./", title = "Select a File", \
        filetypes = (("Text files","*.txt*"),("Executable files","*.exe*"), ("all files","*.*")))
        # Change label contents
        if filename != "":
            self.load_past_data(filename, section)

    #function used to create a file explorer for exe source folder   
    def dir_file_explorer(self, section):
        folderame = askDirectory(initialdir = "./", title = "Select a Folder")
        # Change label contents
        if folderame != "":
            self.load_past_data(folderame, section)

    def create_file_window(self):
        self.new_window = tk.Toplevel(self.frame)
        self.new_window.title("Chosen Files")
        self.new_window_layout(self.new_window)

    def new_window_layout(self, frame):
        self.validate_files()
        self.show_button()
        for i, data in enumerate(self.additionalFileList):
            data_frame = tk.Frame(frame, bg="lightblue")
            data_frame.grid(row=i+1, column=0, sticky="nsew", pady=10)

            path = tk.Label(data_frame, text=data, font=("Arial Bold",12))
            path.grid(row=0, column=0)

            if os.path.exists(data):
                status = tk.Label(data_frame, text="Valid", font=("Arial Bold",12), fg="green")
            else:
                status = tk.Label(data_frame, text="InValid", font=("Arial Bold",12), fg="red")
            status.grid(row=0, column=1)

            remove = tk.Button(data_frame, text="Remove", font=("Arial Bold",12), command=lambda data=data: self.remove_file(data), bg="firebrick1", padx=10)
            remove.grid(row=0, column=2)
        if len(self.additionalFileList) == 0:
            self.new_window.destroy()
    
    def remove_file(self, data):
        self.additionalFileList.remove(data)
        for widget in self.new_window.winfo_children():
            widget.destroy()
        self.new_window_layout(self.new_window)

    def on_entry_focus_in(self, event):
        if event.widget.get() == "Enter Job Title" or event.widget.get() == "Enter Executable Program" \
        or event.widget.get() == "Enter search" or event.widget.get() == "Enter Additional File Aboslute Path" \
        or event.widget.get() == 'Arguments' or event.widget.get() == 'Enter Directory' \
        or event.widget.get() == 'Enter Author\'s Name' or event.widget.get() == 'Number' \
        or event.widget.get() == 'Enter Working Directory':
            event.widget.delete(0, "end")
        
    def remove_page(self):
        for widget in self.frame.winfo_children():
            widget.destroy()

class CompletedTaskTab(tk.Frame):
    def __init__(self, contentFrame, task: TaskState , master=None):
        super().__init__(master)
        self.frame = contentFrame
        self.task: TaskState = task
        self.content = []
        create_grid(self.frame, 30, 30)

    def create_page(self):
        self.collect_all_data()
        status = tk.Label(self.frame, text = "*Completed", fg='green', font=("Arial Bold",12), bg="lightblue")
        status.grid(row=0, column=2, columnspan=2, sticky="w")

        name = tk.Label(self.frame, text = f"{self.main_details[0]}", font=("Arial Bold",20), bg="lightblue")
        name.grid(row=1, column=2, columnspan=2, sticky="w")

        date = tk.Label(self.frame, text = f"{self.main_details[4]}", font=("Arial Bold",12), bg="lightblue")
        date.grid(row=2, column=2, columnspan=2, sticky="w")

        btn_export = tk.Button(self.frame, text="Export task data", font=("Arial Bold", 12),command=self.exportdata_button_clicked)
        btn_export.grid(row=1, column=26, columnspan=3, sticky='ew')

        #this section is for displaying the machines in the task  
        main_Canvas = tk.Canvas(self.frame)
        main_Canvas.grid(row=3, column=2, rowspan=1, columnspan=26, sticky="ew")

        main_content_frame = tk.Frame(main_Canvas)
        main_Canvas.create_window((0, 0), window=main_content_frame)

        self.populate_top_scrollwindow(main_content_frame)

        y_scrollbar = tk.Scrollbar(self.frame, orient="vertical", command=main_Canvas.yview)
        y_scrollbar.grid(row=3, column=29, rowspan=3, sticky="ns")
        main_Canvas.configure(yscrollcommand=y_scrollbar.set)

        #this next section is for the machine 'console'
        main_content_frame.update_idletasks()
        main_Canvas.config(scrollregion=main_Canvas.bbox("all")) 

        self.machine_name = tk.Label(self.frame, text = "Machine ID", font=("Arial Bold",16), bg="lightblue")
        self.machine_name.grid(row=10, column=2, columnspan=2, sticky="w")

        machine_Canvas = tk.Canvas(self.frame)
        machine_Canvas.grid(row=11, column=2, rowspan=10, columnspan=26, sticky="ew")

        machine_content_frame = tk.Frame(machine_Canvas)
        machine_Canvas.create_window((0, 0), window=machine_content_frame)

        self.populate_bottom_scrollwindow(machine_content_frame)

        y_scrollbar = tk.Scrollbar(self.frame, orient="vertical", command=machine_Canvas.yview)
        y_scrollbar.grid(row=11, column=29, rowspan=10, sticky="ns")
        machine_Canvas.configure(yscrollcommand=y_scrollbar.set)

        x_scrollbar = tk.Scrollbar(self.frame, orient="horizontal", command=machine_Canvas.xview)
        x_scrollbar.grid(row=22, column=2, columnspan=26, sticky="ew")
        machine_Canvas.configure(xscrollcommand=x_scrollbar.set)

        machine_content_frame.update_idletasks()
        machine_Canvas.config(scrollregion=machine_Canvas.bbox("all")) 

    def populate_top_scrollwindow(self, frame):
        data_frame = tk.Frame(frame)
        data_frame.grid(row=0, column=0, sticky="nsew")

        for i, jobState in enumerate(self.task.jobList):

            data_frame = tk.Frame(frame)
            data_frame.grid(row=i+1, column=0, sticky="nsew")

            data_labe = tk.Label(data_frame, text=f"Machine: {jobState.clientName}", font=("Arial Bold",16))
            data_labe.grid(row=i+1, column=0, sticky="w")

            inspect_button = tk.Button(data_frame, text='Inspect', font=("Arial Bold",16), command=lambda name=jobState.clientName: self.inspect_button_clicked(name))
            inspect_button.grid(row=i+1, column=2, sticky="e")

    def populate_bottom_scrollwindow(self, frame):
        data_frame = tk.Frame(frame)
        data_frame.grid(row=0, column=0, sticky="nsew")

        for i, data in enumerate(self.content):
            data_frame = tk.Frame(frame)
            data_frame.grid(row=i, column=0, sticky="nsew")

            machine_text = tk.Label(data_frame, text=data, font=("Arial Bold", 12))
            machine_text.grid(row=i, column=0,sticky="w")

    def inspect_button_clicked(self, name):
        self.machine_name["text"] = f"Machine: {name}"
        for job in self.job_data:
            if job[0] == name:
                self.content = job[1]
    
    def collect_all_data(self):
        self.job_data = []
        for jobstate in self.task.jobList:
            machine_data = [jobstate.clientName]
            machine_data_content = []
            while len(jobstate.stdoutQ)>0:
                machine_data_content.append(jobstate.stdoutQ.pop())
            machine_data.append(machine_data_content)
        self.job_data.append(machine_data)

    def exportdata_button_clicked(self):
        print(f"Export data")
    
    def remove_page(self):
        for widget in self.frame.winfo_children():
            widget.destroy()

class RunningTaskTab(tk.Frame):
    def __init__(self, contentFrame, consoleThread: ConsoleThread, task: TaskState, master=None):
        super().__init__(master)
        self.frame = contentFrame
        self.display_data = []
        self.alive_status = []
        self.consoleThread: ConsoleThread = consoleThread
        self.task: TaskState = task

        self.consoleThread.resume_thread()
        create_grid(self.frame, 30, 30)

        for jobState in task.jobList:
            jobState.client.connect()
            jobState.client.create_service()
            jobState.job.start()

        self.initialise_alive_list()
        self.pollTaskStatus()

    def create_page(self):
        status = tk.Label(self.frame, text = "*Running", fg='red', font=("Arial Bold",12), bg="lightblue")
        status.grid(row=0, column=2, columnspan=2, sticky="w")

        name = tk.Label(self.frame, text = self.task.name, font=("Arial Bold",20), bg="lightblue")
        name.grid(row=1, column=2, columnspan=2, sticky="w")

        date = tk.Label(self.frame, text = self.task.startDateTime.strftime("%d/%m/%Y, %H:%M:%S"), font=("Arial Bold",12), bg="lightblue")
        date.grid(row=2, column=2, columnspan=2, sticky="w")

        self.btn_cancel = tk.Button(self.frame, text="Cancel", font=("Arial Bold", 12),command=self.cancel_all_button_clicked)
        self.btn_cancel.grid(row=1, column=26, columnspan=3, sticky='ew')

        #this section is for displaying the machines in the task  
        self.main_Canvas = tk.Canvas(self.frame)
        self.main_Canvas.grid(row=3, column=2, rowspan=1, columnspan=26, sticky="ew")
        self.set_mousewheel(self.main_Canvas, lambda e: self.main_Canvas.config(text=e.delta), 1)

        main_content_frame = tk.Frame(self.main_Canvas)
        self.main_Canvas.create_window((0, 0), window=main_content_frame)

        y_scrollbar = tk.Scrollbar(self.frame, orient="vertical", command=self.main_Canvas.yview)
        y_scrollbar.grid(row=3, column=29, rowspan=3, sticky="ns")
        self.main_Canvas.configure(yscrollcommand=y_scrollbar.set) 

        self.machine_name = tk.Label(self.frame, text='', font=("Arial Bold",16), bg="lightblue")
        self.machine_name.grid(row=10, column=2, columnspan=2, sticky="w")

        self.machine_Canvas = tk.Canvas(self.frame)
        self.machine_Canvas.grid(row=11, column=2, rowspan=10, columnspan=26, sticky="ew")
        self.set_mousewheel(self.machine_Canvas, lambda e: self.machine_Canvas.config(text=e.delta), 2)

        self.machine_content_frame = tk.Frame(self.machine_Canvas)
        self.machine_Canvas.create_window((0, 0), window=self.machine_content_frame)

        y_scrollbar = tk.Scrollbar(self.frame, orient="vertical", command=self.machine_Canvas.yview)
        y_scrollbar.grid(row=11, column=29, rowspan=10, sticky="ns")

        x_scrollbar = tk.Scrollbar(self.frame, orient="horizontal", command=self.machine_Canvas.xview)
        x_scrollbar.grid(row=23, column=2, columnspan=26, sticky="ew")
        self.machine_Canvas.configure(xscrollcommand=x_scrollbar.set)
        self.machine_Canvas.configure(yscrollcommand=y_scrollbar.set)

        self.populate_top_scrollwindow(main_content_frame)

        main_content_frame.update_idletasks()
        self.main_Canvas.config(scrollregion=self.main_Canvas.bbox("all"))

        self.machine_content_frame.update_idletasks()
        self.machine_Canvas.config(scrollregion=self.machine_Canvas.bbox("all"))

        self.console_input = tk.Entry(self.frame, state=tk.DISABLED)
        self.console_input.insert(0, "Enter Standard Input")
        self.console_input.bind("<FocusIn>", self.on_entry_focus_in)
        self.console_input.grid(row=21, column=2, rowspan=2, columnspan=23, sticky="ew")

        self.console_btn = tk.Button(self.frame, text="Send Standard Input", state=tk.DISABLED, font=("Arial Bold", 12),command=self.send_stdin)
        self.console_btn.grid(row=21, column=25)
    
    def recieveData(self, item):
        self.display_data.append(item)
        self.populate_bottom_scrollwindow()
        for i in len(self.alive_status):
            if (self.alive_status[i][0] == self.machine_name.get()):
                if(self.alive_status[i][1] == False):
                    self.taskNotRunning()

    def send_stdin(self):
        input = self.console_input.get()
    
    ####
    #This function is used to see if the task is still running
    ###
    def taskNotRunning(self):
        self.consoleThread.loadQueues(None, None)
        #clears the contents in the bottom scroll wheel, wrights a message to it, and disables the window
        self.display_data = ["THE TASK HAS FINISHED RUNNING. VIEW THE RESULTS IN TASK HISTORY PAGE ONCE ALL MACHINES HAVE FINISHED"]
        self.populate_bottom_scrollwindow()

        self.console_btn.config(state=tk.DISABLED)
        self.console_input.config(state=tk.DISABLED)
        self.checkAllTaskNotRunning()
    
    def checkAllTaskNotRunning(self):
        for data in self.alive_status:
            if data[1] == True:
                return
        self.btn_cancel.config(state=tk.DISABLED)
        self.console_btn.config(state=tk.DISABLED)
        self.console_input.config(state=tk.DISABLED)
            

    def populate_top_scrollwindow(self, frame):
        data_frame = tk.Frame(frame)
        data_frame.grid(row=0, column=0, sticky="nsew")

        for jobState in self.task.jobList:
            name_label = tk.Label(data_frame, text=jobState.clientName, font=("Arial Bold", 16))
            name_label.grid(row=1, column=0, sticky="w")

            inspect_button = tk.Button(data_frame, text='Inspect', font=("Arial Bold",16), command=lambda clientName=jobState.clientName : self.inspect_button_clicked(clientName))
            inspect_button.grid(row=1, column=1, sticky="e")

    def populate_bottom_scrollwindow(self):
        for widget in self.machine_content_frame.winfo_children():
            widget.destroy()
        for i, content in enumerate(self.display_data):
            data_frame = tk.Frame(self.machine_content_frame)
            data_frame.grid(row=i, column=0, sticky="ew")
            machine_text = tk.Label(data_frame, text=self.display_data[i], font=("Arial Bold", 12))
            machine_text.grid(row=0, column=0,sticky="w")
        self.machine_content_frame.update_idletasks()
        self.machine_Canvas.config(scrollregion=self.machine_Canvas.bbox("all")) 

    def set_mousewheel(self, widget, command, canvas):
        if canvas == 2:
            widget.bind("<Enter>", lambda _: widget.bind_all('<MouseWheel>', self._on_mousewheel_canvas2))
            widget.bind("<Leave>", lambda _: widget.unbind_all('<MouseWheel>'))
        elif canvas == 1:
            widget.bind("<Enter>", lambda _: widget.bind_all('<MouseWheel>', self._on_mousewheel_canvas1))
            widget.bind("<Leave>", lambda _: widget.unbind_all('<MouseWheel>'))
    
    def _on_mousewheel_canvas2(self, event):
        content_height = self.machine_Canvas.bbox("all")[3] - self.machine_Canvas.bbox("all")[1]
        visible_height = self.machine_Canvas.winfo_height()
        if content_height > visible_height:
            self.machine_Canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        else:
            self.machine_Canvas.yview_moveto(0)
    
    def _on_mousewheel_canvas1(self, event):
        content_height = self.main_Canvas.bbox("all")[3] - self.main_Canvas.bbox("all")[1]
        visible_height = self.main_Canvas.winfo_height()
        if content_height > visible_height:
            self.main_Canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        else:
            self.main_Canvas.yview_moveto(0)

    def inspect_button_clicked(self, clientName: str):
        for i,jobState in enumerate(self.task.jobList):
            if jobState.clientName == clientName: 
                if self.alive_status[i][1] == True:
                    self.consoleThread.loadQueues(jobState.stdoutQ, jobState.stdinQ)
                    self.display_data = [] #clears the scroll window. will replace with saved data later
                    self.populate_bottom_scrollwindow()
                    self.machine_name.insert(0,jobState.clientName)
                    self.console_btn.config(state=tk.NORMAL)
                    self.console_input.config(state=tk.NORMAL)
                    break
                else:
                    self.taskNotRunning()            

    def cancel_all_button_clicked(self):
        for jobState in self.task.jobList:
            jobState.job.cancel()
            jobState.job.join()

    def pollTaskStatus(self):
        for i,jobState in enumerate(self.task.jobList):
            if jobState.job.is_alive():
                self.alive_status[i][1] = True
            else:
                self.alive_status[i][1] = False
                
        self.frame.after(5000, self.pollTaskStatus)
    
    def initialise_alive_list(self):
        for jobState in self.task.jobList:
            if jobState.job.is_alive():
                self.alive_status.append(jobState.clientName, True)
            else:
                self.alive_status.append(jobState.clientName, False)
    
    def on_entry_focus_in(self, event):
        if event.widget.get() == "Enter Command":
            event.widget.delete(0, "end")
    
    def remove_page(self):
        self.consoleThread.pause_thread()
        for widget in self.frame.winfo_children():
            widget.destroy()
