import os
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from tkinter.filedialog import askdirectory as askDirectory
from PIL import Image, ImageTk

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
        DATA = []
        for i in range(24):
            testData = {"NAME": f"PC{i+1}", "IP": f"10.0.2.{i}"}
            DATA.append(testData)
        return DATA

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
    
    #function is used to add or remove a PC for the chosen pc list depending on if it has been pressed or is user checked the select all machines button
    #takes in the index of a button in the pc_button list, and a boolean (true if just one button, false if called by select_all_machines)
    def add_pc_to_list(self, button_index, individual):
        button = self.pc_buttons[button_index]
        button_text = button.cget("text")
        current_relief = button.cget("relief")  # Get current relief style
        if current_relief == "raised" and individual:
            new_relief = "sunken"
            self.chosen_pc.append(button_text)
        elif current_relief == "sunken" and individual:
            new_relief = "raised"
            if button_text in self.chosen_pc:
                self.chosen_pc.remove(button_text)
                self.AllMachines.set("False")
        elif  self.AllMachines.get() == True and not individual:
            new_relief = "sunken"
            if button_text not in self.chosen_pc:
                self.chosen_pc.append(button_text)
        elif  self.AllMachines.get() == False and not individual:
            new_relief = "raised"
            if button_text in self.chosen_pc:
                self.chosen_pc.remove(button_text)

        self.show_button()
        button.config(relief=new_relief)

    def show_button(self):
        if len(self.chosen_pc) > 0:
            self.create_job.config(state=tk.NORMAL)
        else:
            self.create_job.config(state=tk.DISABLED)

    def create_page(self):
        title = tk.Label(self.frame, text = "Active Directory", font=("Arial Bold",20), bg="lightblue")
        title.grid(row=0, column=2, columnspan=2, sticky="w")

        #checkbox button for selecting all machines listed
        self.AllMachines = tk.BooleanVar()
        select_all_button = ttk.Checkbutton(self.frame, text="Select All Machines", variable=self.AllMachines, onvalue=True, offvalue=False, command=self.select_all_machines)
        select_all_button.grid(row=1, column=7)

        self.create_job = ttk.Button(self.frame, text="Create New Job", state=tk.DISABLED, command=self.call_create_job_callback)
        self.create_job.grid(row=1, column=9, columnspan=1)
        
        # Create a Canvas widget for scrollable content
        canvas = tk.Canvas(self.frame)
        canvas.grid(row=2, column=2, rowspan=26, columnspan=26, sticky="nsew")

        #collect machine list from active directory
        self.machine_list = self.gather_machines()
        num_rows = (len(self.machine_list)//5 + 1)

        # Create a Frame to contain the actual content
        content_frame = tk.Frame(canvas)
        create_grid(content_frame, num_rows, 5)
        canvas.create_window((0, 0), window=content_frame)

        # Define constants for layout
        num_per_row = 5
        spacing = 25  # Adjust as needed

        for i, data in enumerate(self.machine_list):
            
            # Calculate row and column based on index
            row = (i // num_per_row)*2
            col = i % num_per_row

            sub_frame = tk.Frame(content_frame)  # Create a sub-frame for each button-label pair
            sub_frame.grid(row=row, column=col, padx=spacing, pady=spacing)

            pc_btn = tk.Button(sub_frame, text=data["NAME"], command=lambda i=i: self.add_pc_to_list(i, True))
            pc_btn.grid(row=0, column=0)
            self.pc_buttons.append(pc_btn)

            label = tk.Label(sub_frame, text="IP: "+ data["IP"])
            label.grid(row=1, column=0)

            # Calculate the width of sub_frame after it's been created
            sub_frame.update_idletasks()
            sub_frame_width = sub_frame.winfo_width()

            # Set padx to be half of the remaining space to center sub_frame
            remaining_space = (canvas.winfo_width() - num_per_row * sub_frame_width) // (num_per_row + 1)
            padx = max(0, remaining_space // 2)

            # Update padx for sub_frame
            sub_frame.grid_configure(padx=padx)
        


        # Add scrollbars
        y_scrollbar = tk.Scrollbar(self.frame, orient="vertical", command=canvas.yview)
        y_scrollbar.grid(row=2, column=29, rowspan=27, sticky="ns")
        canvas.configure(yscrollcommand=y_scrollbar.set)

        x_scrollbar = tk.Scrollbar(self.frame, orient="horizontal", command=canvas.xview)
        x_scrollbar.grid(row=29, column=2, columnspan=27, sticky="ew")
        canvas.configure(xscrollcommand=x_scrollbar.set) 

        # Update scrollable region
        content_frame.update_idletasks()
        canvas.config(scrollregion=canvas.bbox("all")) 


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

    #creats a call back function to pass data back to tab_manager
    def call_create_job_callback(self, job_path):
        self.create_job_callback(job_path)
    
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

        self.search_directory()

        content_frame = tk.Frame(canvas)
        canvas.create_window((0, 0), window=content_frame)

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

    #searches the task_history_file folder (assuming that were all the taks will be stored)
    def search_directory(self):
        self.past_jobs = []
        for filename in os.listdir("./task_history_files/"):
            if filename.endswith(".txt"):
                file_path = os.path.join("./task_history_files/", filename)
                self.process_text_file(file_path)

    #collects data from the files (assuming first 3 lines hold all neccessary info)
    def process_text_file(self, file_path):
        with open(file_path, 'r') as file:
            data = file.read().splitlines()

            #this removes all the absoulte path address from the program (just for displaying)
            #this if statement takes into account path names used either / or \
            index = data[2].rfind("\\")
            if index == -1:
                index = data[2].rfind("/")
            program = data[2][index+1:]
            job = {"NAME": data[0], "NUM_COMP": data[1], "PROGRAM": program, "DATE": data[4], "PATH": file_path}
            self.past_jobs.append(job)

    #fill in the scroll window with all the info from the task stored in the task_history_file folder
    def populate_scrollwindow(self, canvas):
        data_frame = tk.Frame(canvas)
        for i in range(5):
            data_frame.grid_columnconfigure(i, weight=1)
        data_frame.grid(row=0, column=0, sticky="nsew")
        


        for i, data in enumerate(self.past_jobs):
            data_elements = [
                f"Name: {data['NAME']}",
                f"Number of Machines: {data['NUM_COMP']}",
                f"Date Started: {data['DATE']}",
                f"Program: {data['PROGRAM']}"
            ]

            # create LabelFrame for job
            job_frame = tk.LabelFrame(data_frame, text=f"Job {i + 1}", font=("Arial Bold", 12))
            job_frame.grid(row=i+1, column=0, sticky="nsew", padx=10, pady=10)

            for k, obj in enumerate(data_elements):
                info = tk.Label(job_frame, text=obj, font=("Arial Bold", 12))
                info.grid(row=0, column=k, sticky="w")
                job_frame.grid_columnconfigure(k, weight=1)
      

            button = tk.Button(job_frame, text=f"Inspect {data['NAME']}", command=lambda path=data["PATH"]: self.call_create_job_callback(path))
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
        self.validFiles = True
        self.additionalFileList = []
        create_grid(self.frame, 30, 30)

    def create_page(self):
        main_title = tk.Label(self.frame, text = "Job Configuration", font=("Arial Bold",20), bg="lightblue")
        main_title.grid(row=0, column=2, columnspan=2, sticky="w")

        #this section is for the author's name input 
        author_title = tk.Label(self.frame, text="Author Name:", font=("Arial Bold",12), bg="lightblue")
        author_title.grid(row=1, column=2, columnspan=19)

        self.author_input = tk.Entry(self.frame)
        self.author_input.insert(0, "Enter Author's Name")
        self.author_input.bind("<FocusIn>", self.on_entry_focus_in)
        self.author_input.grid(row=2, column=2, columnspan=19, sticky="ew")

        name_title = tk.Label(self.frame, text="Task Name:", font=("Arial Bold",12), bg="lightblue")
        name_title.grid(row=3, column=2, columnspan=19)

        #this section is for the name input and calls functions to make sure its valid
        self.name_input = tk.Entry(self.frame)
        self.name_input.insert(0, "Enter Job Title")
        self.name_input.bind("<FocusIn>", self.on_entry_focus_in)
        self.name_input.grid(row=4, column=2, columnspan=19, sticky="ew")
        reg1 = self.name_input.register(self.validate_name)
        self.name_input.config(validate ="key", validatecommand =(reg1, '%P'))

        self.valid_name = tk.Label(self.frame, font=("Arial Bold",12), fg="lightgreen", bg='lightblue')
        self.valid_name.grid(row=5, column=2, columnspan=19)

        #program absoulute path title
        program_title = tk.Label(self.frame, text="Executable:", font=("Arial Bold",12), bg="lightblue")
        program_title.grid(row=6, column=2, columnspan=19)

        #this section is for the program path input and calls functions to make sure its valid
        self.program_input = tk.Entry(self.frame)
        self.program_input.insert(0, "Enter Executable Program")
        self.program_input.bind("<FocusIn>", self.on_entry_focus_in)
        self.program_input.grid(row=7, column=2, columnspan=19, sticky="ew")
        reg2 = self.frame.register(self.check_program)
        self.program_input.config(validate ="key", validatecommand =(reg2, '%P'))

        ##
        #section is for executabe arguments
        ##

        arg_title = tk.Label(self.frame, text="Arguments", font=("Arial Bold",12), bg="lightblue")
        arg_title.grid(row=8, column=2, columnspan=19)

        self.arg_input = tk.Entry(self.frame)
        self.arg_input.insert(0, "Arguments:")
        self.arg_input.bind("<FocusIn>", self.on_entry_focus_in)
        self.arg_input.grid(row=9, column=2, columnspan=19, sticky="ew")


        #check button for making sure if program in on local machine or remote
        self.localMachine = tk.BooleanVar()
        #initially set to false
        self.localMachine.set("False")
        localMachine_option_button = ttk.Checkbutton(self.frame, text="Select Program on Local Machine", variable=self.localMachine, onvalue=True, offvalue=False, command=self.local_machine_option)
        localMachine_option_button.grid(row=11, column=2, columnspan=8)

        #button used to open a file explorer
        self.button_explore = ttk.Button(self.frame, text = "Browse Files", state=tk.DISABLED, command=lambda i=1: self.dir_file_explorer(i))
        self.button_explore.grid(row=11, column=10, columnspan=8)

        ##
        #section is for local exe source directory
        ##

        exe_dir_title = tk.Label(self.frame, text="Local Executable Source Directory", font=("Arial Bold",12), bg="lightblue")
        exe_dir_title.grid(row=12, column=2, columnspan=19)

        self.exe_dir_input = tk.Entry(self.frame)
        self.exe_dir_input.insert(0, "Enter Directory")
        self.exe_dir_input.bind("<FocusIn>", self.on_entry_focus_in)
        self.exe_dir_input.config(state=tk.DISABLED)
        self.exe_dir_input.grid(row=13, column=2, columnspan=19, sticky="ew")
        reg4 = self.frame.register(self.check_path)
        self.exe_dir_input.config(validate ="key", validatecommand =(reg4, '%P'))

        #used to display to user if path for executable entered is valid
        self.valid_path = tk.Label(self.frame, font=("Arial Bold",12), fg="lightgreen", bg='lightblue')
        self.valid_path.grid(row=14, column=2, columnspan=19)
        
        #check button for running program as system admin
        self.sysAdmin = tk.BooleanVar()
        #initially set to false
        self.sysAdmin.set("False")
        sysAdmin_button = ttk.Checkbutton(self.frame, text="Run Program as System Admin", variable=self.sysAdmin, onvalue=True, offvalue=False)
        sysAdmin_button.grid(row=15, column=2, columnspan=19)

        ##
        #adding additional files to be sent over
        ##

        #used to check if user wants to send over additional files
        self.additionalFile = tk.BooleanVar()
        self.additionalFile.set("False")
        additionalFile_option_button = ttk.Checkbutton(self.frame, text="Send Additional Files", variable=self.additionalFile, onvalue=True, offvalue=False, command=self.additional_file_option)
        additionalFile_option_button.grid(row=17, column=2, columnspan=19)

        #file absoulute path title
        file_title = tk.Label(self.frame, text="Files's Absolute Path:", font=("Arial Bold",12), bg="lightblue")
        file_title.grid(row=18, column=2, columnspan=19)

        #Used to all user to enter additional files
        self.additionalFile_input = tk.Entry(self.frame)
        self.additionalFile_input.insert(0, "Enter Additional File Aboslute Path")
        self.additionalFile_input.bind("<FocusIn>", self.on_entry_focus_in)
        self.additionalFile_input.config(state=tk.DISABLED)
        self.additionalFile_input.grid(row=19, column=2, columnspan=19, sticky="ew")
        reg3 = self.frame.register(self.validate_file_path)
        self.additionalFile_input.config(validate ="key", validatecommand =(reg3, '%P'))

        self.valid_additionalFile_path = tk.Label(self.frame, font=("Arial Bold",12), fg="green", bg='lightblue')
        self.valid_additionalFile_path.grid(row=20, column=2, columnspan=19)

        #button used to add file to list of other additional files
        self.additionalFile_Button = ttk.Button(self.frame, text="Add File", state=tk.DISABLED, command=self.add_additional_file)
        self.additionalFile_Button.grid(row=21, column=2, columnspan=19)

        #button used to open a file explorer for additional files
        self.additionalFiles_button_explore = ttk.Button(self.frame, text = "Browse Files", state=tk.DISABLED, command=lambda i=2: self.file_explorer(i))
        self.additionalFiles_button_explore.grid(row=22, column=2, columnspan=19)

        #button used to view all additional files added so far
        self.additionalFile_view_Button = ttk.Button(self.frame, text="View All Additional Files Chosen", state=tk.DISABLED, command=self.create_file_window)
        self.additionalFile_view_Button.grid(row=23, column=2, columnspan=19)

        self.valid_additionalFiles = tk.Label(self.frame, font=("Arial Bold",12), fg="green", bg='lightblue')
        self.valid_additionalFiles.grid(row=25, column=2, columnspan=19)


        #create job button
        self.create_job = ttk.Button(self.frame, text="Create New Job", state=tk.DISABLED, command=self.call_create_job_callback)
        self.create_job.grid(row=26, column=2, columnspan=19)


        #past job config side of page
        side_title = tk.Label(self.frame, text = "Past Job Configuration", font=("Arial Bold",16), bg="lightblue")
        side_title.grid(row=0, column=23, columnspan=2, sticky="w")

        self.search_bar = tk.Entry(self.frame)
        self.search_bar.insert(0, "Enter search")
        self.search_bar.bind("<FocusIn>", self.on_entry_focus_in)
        self.search_bar.grid(row=1, column=23, columnspan=2, sticky="ew")

        self.canvas = tk.Canvas(self.frame)
        self.canvas.grid(row=2, column=23, rowspan=14, columnspan=5, sticky="nsew")
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
        self.canvas2.grid(row=17, column=23, rowspan=12, columnspan=5, sticky="nsew")
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

    #used to change state of button_explore
    def local_machine_option(self):
        if self.localMachine.get():
            self.button_explore.config(state=tk.NORMAL)
            self.exe_dir_input.config(state=tk.NORMAL)
            path = self.exe_dir_input.get() + "/" + self.program_input.get()
            path.replace('\\','/')
            self.validate_path(path)
        else:
            self.button_explore.config(state=tk.DISABLED)
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
        if self.validName and self.validPath and not self.additionalFile.get():
            self.create_job.config(state=tk.NORMAL)
        elif self.validName and self.validPath and self.additionalFile.get() and self.validFiles:
            self.create_job.config(state=tk.NORMAL)
        else:
            self.create_job.config(state=tk.DISABLED)
    
    #function used to send data back to tab_manager
    def call_create_job_callback(self):
        self.validate_files()
        if (self.validName and self.validPath and not self.additionalFile.get()) or (self.validName and self.validPath and self.additionalFile.get() and self.validFiles):
            arguments = self.arg_input.get()
            author = self.author_input.get()
            if arguments == "Arguments:":
                arguments = ''
            if author == 'Enter Author\'s Name':
                author = ''
            results = {"AUTHOR" : author,
                    "NAME": self.name_input.get(), 
                    "PROGRAM": self.program_input.get(),
                    "ARGUMENTS": arguments,
                    "SYSADMIN": self.sysAdmin.get(), 
                    "LOCALMACHINE": self.localMachine.get(), 
                    "ADDFILES": [],
                    "PCs": self.chosen_pc}
            if self.additionalFile.get() and self.localMachine.get():
                results["PROGRAM"] = self.exe_dir_input.get() + "/" + self.program_input.get()
                results["ADDFILES"] = self.additionalFileList
            elif not self.additionalFile.get() and self.localMachine.get():
                results["PROGRAM"] = self.exe_dir_input.get() + "/" + self.program_input.get()
            elif self.additionalFile.get() and not self.localMachine.get():
                results["ADDFILES"] = self.additionalFileList
            self.create_job_callback(results)

    #function used to create a file explorer    
    def file_explorer(self, section):
        filename = filedialog.askopenfilename(initialdir = "./", title = "Select a File", filetypes = (("Text files","*.txt*"),("Executable files","*.exe*"), ("all files","*.*")))
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
        if event.widget.get() == "Enter Job Title" or event.widget.get() == "Enter Executable Program" or event.widget.get() == "Enter search" or event.widget.get() == "Enter Additional File Aboslute Path" or event.widget.get() == 'Arguments:' or event.widget.get() == 'Enter Directory' or event.widget.get() == 'Enter Author\'s Name':
            event.widget.delete(0, "end")
        
    def remove_page(self):
        for widget in self.frame.winfo_children():
            widget.destroy()


class completedTab(tk.Frame):
    def __init__(self, contentFrame, job_path, master=None):
        super().__init__(master)
        self.frame = contentFrame
        self.job_path = job_path
        create_grid(self.frame, 30, 30)

    def create_page(self):
        self.gather_file_details()

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
        

    def gather_file_details(self):
        self.main_details = []
        self.machine_details = []
        with open(self.job_path, 'r') as file:
            name = file.readline()[:-1]
            num_computers = file.readline()[:-1]
            program = file.readline()[:-1]
            status = file.readline()[:-1]
            date = file.readline()[:-1]
            self.main_details.append(name)
            self.main_details.append(num_computers)
            self.main_details.append(program)
            self.main_details.append(status)
            self.main_details.append(date)

            for f in file:
                split = f[:-1].split('|')
                machine = {"NAME": split[0], "IP": split[1], "CONTENTS": split[2]}
                self.machine_details.append(machine)

    def populate_top_scrollwindow(self, frame):
        data_frame = tk.Frame(frame)
        data_frame.grid(row=0, column=0, sticky="nsew")



        for i, data in enumerate(self.machine_details):

            data_frame = tk.Frame(frame)
            data_frame.grid(row=i+1, column=0, sticky="nsew")

            data_label = tk.Label(data_frame, text=f"Machine: {data['NAME']}", font=("Arial Bold",16))
            data_label.grid(row=i+1, column=0, sticky="w")

            data_labe2 = tk.Label(data_frame, text=f"IP: {data['IP']}", font=("Arial Bold",16))
            data_labe2.grid(row=i+1, column=1, sticky="w")

            inspect_button = tk.Button(data_frame, text='Inspect', font=("Arial Bold",16), command=lambda name=data['NAME'], contents= data['CONTENTS']: self.inspect_button_clicked(name,contents))
            inspect_button.grid(row=i+1, column=2, sticky="e")

    def populate_bottom_scrollwindow(self, frame):
        data_frame = tk.Frame(self.frame)
        data_frame.grid(row=7, column=2, rowspan=10, columnspan=26, sticky="ew")
        self.machine_text = tk.Label(data_frame, text="", font=("Arial Bold", 12))
        self.machine_text.grid(row=0, column=0,sticky="w")

   
  
        

    def inspect_button_clicked(self, name, contents):
        self.machine_text["text"] = contents
        self.machine_name["text"] = f"Machine: {name}"

        
        


    def exportdata_button_clicked(self):
        print(f"Export data")
    
    def remove_page(self):
        for widget in self.frame.winfo_children():
            widget.destroy()
