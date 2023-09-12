import os
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk

#used to create grid used in the frames
def create_grid(frame, rows, columns):
    for i in range(rows):
        frame.grid_rowconfigure(i, weight=1)
        for j in range(columns):
            frame.grid_columnconfigure(j, weight=1)
def resize_image(image, width, height):
        return image.resize((width, height), Image.ANTIALIAS)



class ADTab(tk.Frame):
    def __init__(self, contentFrame, create_job_callback, master=None):
        super().__init__(master)
        self.frame = contentFrame
        self.create_job_callback = create_job_callback
        create_grid(self.frame, 12, 12)
        self.pc_buttons = []
        self.chosen_pc = []

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
        title = ttk.Label(self.frame, text = "Active Directory")
        title.grid(row=0, column=2, columnspan=2, sticky="w")

        #checkbox button for selecting all machines listed
        self.AllMachines = tk.BooleanVar()
        select_all_button = ttk.Checkbutton(self.frame, text="Select All Machines", variable=self.AllMachines, onvalue=True, offvalue=False, command=self.select_all_machines)
        select_all_button.grid(row=1, column=7)

        self.create_job = ttk.Button(self.frame, text="Create New Job", state=tk.DISABLED, command=self.call_create_job_callback)
        self.create_job.grid(row=1, column=9, columnspan=1)
        
        # Create a Canvas widget for scrollable content
        canvas = tk.Canvas(self.frame)
        canvas.grid(row=2, column=2, rowspan=8, columnspan=8, sticky="nsew")

        #collect machine list from active directory
        self.machine_list = self.gather_machines()
        num_rows = (len(self.machine_list)//5 + 1)

        # Create a Frame to contain the actual content
        content_frame = tk.Frame(canvas)
        create_grid(content_frame, num_rows, 5)
        canvas.create_window((0, 0), window=content_frame)

        pc_image1 = Image.open("desktop-outline.png")

        pc_img1 = ImageTk.PhotoImage(resize_image(pc_image1, 100, 100))

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


        # Add scrollbars
        y_scrollbar = tk.Scrollbar(self.frame, orient="vertical", command=canvas.yview)
        y_scrollbar.grid(row=2, column=10, rowspan=8, sticky="ns")
        canvas.configure(yscrollcommand=y_scrollbar.set)

        x_scrollbar = tk.Scrollbar(self.frame, orient="horizontal", command=canvas.xview)
        x_scrollbar.grid(row=10, column=2, columnspan=8, sticky="ew")
        canvas.configure(xscrollcommand=x_scrollbar.set)

        # Configure mouse wheel scrolling
        def on_mousewheel(event):
            if event.delta > 0:
                canvas.yview_scroll(-1 * (event.delta // 120), "units")
            else:
                canvas.yview_scroll(1 * (abs(event.delta) // 120), "units")
            canvas.xview_scroll(-1 * (event.delta // 120), "units")
        canvas.bind_all("<MouseWheel>", on_mousewheel)  

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
        create_grid(self.frame, 12, 12)

    #creats a call back function to pass data back to tab_manager
    def call_create_job_callback(self, job_path):
        self.create_job_callback(job_path)
    
    #shows whats in the search bar
    def display_search(self):
        search_text = self.search_bar.get()
        print(search_text)

    def create_page(self):
        title = ttk.Label(self.frame, text = "Task History")
        title.grid(row=0, column=2, columnspan=2, sticky="w")

        # Left side
        self.search_bar = tk.Entry(self.frame)
        self.search_bar.insert(0, "Enter search")
        self.search_bar.grid(row=1, column=2, columnspan=4, sticky="ew")

        search_bar_btn = ttk.Button(self.frame, text="Search", command=self.display_search)
        search_bar_btn.grid(row=1, column=7, columnspan=2, sticky="ew")

        canvas = tk.Canvas(self.frame)
        canvas.grid(row=2, column=2, rowspan=8, columnspan=8, sticky="nsew")

        self.search_directory()

        content_frame = tk.Frame(canvas)
        canvas.create_window((0, 0), window=content_frame)

        self.populate_scrollwindow(content_frame)

        #for scroll bars
        y_scrollbar = tk.Scrollbar(self.frame, orient="vertical", command=canvas.yview)
        y_scrollbar.grid(row=2, column=10, rowspan=8, sticky="ns")
        canvas.configure(yscrollcommand=y_scrollbar.set)

        x_scrollbar = tk.Scrollbar(self.frame, orient="horizontal", command=canvas.xview)
        x_scrollbar.grid(row=10, column=2, columnspan=8, sticky="ew")
        canvas.configure(xscrollcommand=x_scrollbar.set)

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
            job = {"NAME": data[0], "NUM_COMP": data[1], "PROGRAM": data[2], "PATH": file_path}
            self.past_jobs.append(job)

    #fill in the scroll window with all the info from the task stored in the task_history_file folder
    def populate_scrollwindow(self, frame):
        data_frame = tk.Frame(frame)
        data_frame.grid(row=0, column=0, sticky="nsew")

        #this is used to allow the frame to spread out horizontally more
        data_label = tk.Label(data_frame, text=str("-"*125), bg="lightblue")
        data_label.grid(row=0, column=0, sticky="nsew")
      
        for i, data in enumerate(self.past_jobs):
            concatenated_data = f"{data['NAME']}, Number of Machines: {data['NUM_COMP']}, Program: {data['PROGRAM']}"

            data_frame = tk.Frame(frame)
            data_frame.grid(row=i+1, column=0, sticky="nsew")

            data_label = tk.Label(data_frame, text=data['NAME'], bg="lightblue")
            data_label.grid(row=i+1, column=0, sticky="w")

            data_labe2 = tk.Label(data_frame, text=f"Number of Machines: {data['NUM_COMP']}", bg="lightblue")
            data_labe2.grid(row=i+1, column=1, sticky="w")

            data_labe3 = tk.Label(data_frame, text=f"Program: {data['PROGRAM']}", bg="lightblue")
            data_labe3.grid(row=i+1, column=2, sticky="w")
            

            button = tk.Button(data_frame, text=f"Inspect {data['NAME']}", command= lambda path=data["PATH"]: self.call_create_job_callback(path))
            button.grid(row=i+1, column=3, sticky="e")

            data_frame.grid_columnconfigure(0, weight=1)
            data_frame.grid_columnconfigure(1, weight=1)
    
    
    def remove_page(self):
        for widget in self.frame.winfo_children():
            widget.destroy()


class JCTab(tk.Frame):
    def __init__(self, contentFrame,create_job_callback, master=None):
        super().__init__(master)
        self.frame = contentFrame
        self.create_job_callback = create_job_callback
        create_grid(self.frame, 12, 12)
        

    #creats a call back function to pass data back to tab_manager
    def call_create_job_callback(self, job_path):
        self.create_job_callback(job_path)
    
    #shows whats in the search bar
    def display_search(self):
        search_text = self.search_bar.get()
        print(search_text)

    def create_page(self):
        title = ttk.Label(self.frame, text = "Job Created")
        title.grid(row=0, column=2, columnspan=2, sticky="w")
        # Job input
        Job_tittle = ttk.Label(self.frame, text = "Job")
        Job_tittle .grid(row=1, column=0, columnspan=1, sticky="w")
        self.job_entry = tk.Entry(self.frame)
        self.job_entry.insert(0, "Enter Job")
        self.job_entry.bind("<FocusIn>", self.on_entry_focus_in)
        self.job_entry.bind("<FocusOut>", self.on_entry_focus_out)
        self.job_entry.grid(row=1, column=2, columnspan=2, sticky="ew")

        # Program input
        Program_tittle = ttk.Label(self.frame, text = "Program")
        Program_tittle .grid(row=2, column=0, columnspan=1, sticky="w")

        self.program_entry = tk.Entry(self.frame)
        self.program_entry.insert(0, "Enter Program")
        self.program_entry.bind("<FocusIn>", self.on_entry_focus_in)
        self.program_entry.bind("<FocusOut>", self.on_entry_focus_out)
        self.program_entry.grid(row=2, column=2, columnspan=2, sticky="ew")

        # Create Job button
        create_job_btn = ttk.Button(self.frame, text="Create Job",command=self.create_job)
        #command= lambda path=data["PATH"]: self.call_create_job_callback(path)
        create_job_btn.grid(row=3, column=2,rowspan=2, columnspan=2, sticky="ew")
        
        # past job config
        past_job_config = ttk.Label(self.frame, text = "Past Job Config")
        past_job_config .grid(row=0, column=9, columnspan=1, sticky="w")
        self.search_bar = tk.Entry(self.frame)
        self.search_bar.insert(0, "Enter search")
        self.search_bar.bind("<FocusIn>", self.on_entry_focus_in)
        self.search_bar.bind("<FocusOut>", self.on_entry_focus_out)
        self.search_bar.grid(row=1, column=9, columnspan=2, sticky="ew")

        search_bar_btn = ttk.Button(self.frame, text="Search", command=self.display_search)
        search_bar_btn.grid(row=2, column=9, columnspan=2, sticky="ew")
        
        #output
        canvas = tk.Canvas(self.frame)
        canvas.grid(row=3, column=9, rowspan=8, columnspan=2, sticky="nsew")

        self.search_directory()

        content_frame = tk.Frame(canvas)
        canvas.create_window((0, 0), window=content_frame)

        self.populate_scrollwindow(content_frame)

        #for scroll bars
        y_scrollbar = tk.Scrollbar(self.frame, orient="vertical", command=canvas.yview)
        y_scrollbar.grid(row=3, column=11, rowspan=8, sticky="ns")
        canvas.configure(yscrollcommand=y_scrollbar.set)

        x_scrollbar = tk.Scrollbar(self.frame, orient="horizontal", command=canvas.xview)
        x_scrollbar.grid(row=11, column=9, columnspan=2, sticky="ew")
        canvas.configure(xscrollcommand=x_scrollbar.set)

        content_frame.update_idletasks()
        canvas.config(scrollregion=canvas.bbox("all")) 

  

    def search_directory(self, keyword=None):
        self.past_jobs = []
        for filename in os.listdir("./task_history_files/"):
            if filename.endswith(".txt"):
                file_path = os.path.join("./task_history_files/", filename)
                if keyword is None or self.file_contains_keyword(file_path, keyword):
                    self.process_text_file(file_path)

    def file_contains_keyword(self, file_path, keyword):
        with open(file_path, 'r') as file:
            data = file.read()
            return keyword in data

    def process_text_file(self, file_path):
        with open(file_path, 'r') as file:
            data = file.read().splitlines()
            job = {"NAME": data[0], "NUM_COMP": data[1], "PROGRAM": data[2], "PATH": file_path}
            self.past_jobs.append(job)
            
    #fill in the scroll window with all the info from the task stored in the task_history_file folder
    def populate_scrollwindow(self, frame):
        data_frame = tk.Frame(frame)
        data_frame.grid(row=0, column=0, sticky="nsew")


        frame.grid_columnconfigure(0, weight=1)

        for i, data in enumerate(self.past_jobs):
            data_frame = tk.Frame(frame)
            data_frame.grid(row=i+1, column=0, sticky="nsew")

            data_label = tk.Label(data_frame, text=data['NAME'], bg="lightblue")
            data_label.grid(row=i+1, column=0, sticky="w")


            data_labe3 = tk.Label(data_frame, text=f"Program: {data['PROGRAM']}", bg="lightblue")
            data_labe3.grid(row=i+1, column=2, sticky="w")

            button = tk.Button(data_frame, text=f"Inpect {data['NAME']}", command=lambda path=data["PATH"]: self.call_create_job_callback(path))
            button.grid(row=i+1, column=3, sticky="e")


            data_frame.grid_columnconfigure(0, weight=1)
            data_frame.grid_columnconfigure(1, weight=1)
            data_frame.grid_columnconfigure(2, weight=1)

    def on_entry_focus_in(self, event):
        if event.widget.get() == "Enter Job Title" or event.widget.get() == "Enter Program" or event.widget.get() == "Enter search":
            event.widget.delete(0, "end")

    def on_entry_focus_out(self, event):
        if event.widget.get() == "":
            if event.widget == self.job_entry:
                event.widget.insert(0, "Enter Job Title")
            elif event.widget == self.program_entry:
                event.widget.insert(0, "Enter Program")
            elif event.widget == self.search_bar:
                event.widget.insert(0, "Enter search")
        event.widget.configure(fg='gray')
    def create_job(self):
        job_title = self.job_title_entry.get()
        if job_title:
            self.create_job_callback(job_title)

    def remove_page(self):
        for widget in self.frame.winfo_children():
            widget.destroy()


class completedTab(tk.Frame):
    def __init__(self, contentFrame, job_path, master=None):
        super().__init__(master)
        self.frame = contentFrame
        self.job_path = job_path
        create_grid(self.frame, 12, 12)

    def create_page(self):
        self.gather_file_details()
        status = tk.Label(self.frame, text = "*Completed", fg='green', font=("Arial Bold",12))
        status.grid(row=0, column=2, columnspan=2, sticky="w")
        name = tk.Label(self.frame, text = f"{self.main_details[0]}", font=("Arial Bold",20))
        name.grid(row=1, column=2, columnspan=2, sticky="w")
       
        date = tk.Label(self.frame, text = "DATE", font=("Arial Bold",12))
        date.grid(row=2, column=2, columnspan=2, sticky="w")

        btn_export = tk.Button(self.frame, text="Export task data", font=("Arial Bold", 12),command=self.exportdata_button_clicked)
        btn_export.grid(row=1, column=10, columnspan=2, sticky='ew')

            
        #this section is for displaying the machines in the task  
        main_Canvas = tk.Canvas(self.frame)
        main_Canvas.grid(row=3, column=2, rowspan=1, columnspan=9, sticky="ew")

        main_content_frame = tk.Frame(main_Canvas)
        main_Canvas.create_window((0, 0), window=main_content_frame)

        self.populate_top_scrollwindow(main_content_frame)

        y_scrollbar = tk.Scrollbar(self.frame, orient="vertical", command=main_Canvas.yview)
        y_scrollbar.grid(row=3, column=11, rowspan=1, sticky="ns")
        main_Canvas.configure(yscrollcommand=y_scrollbar.set)

        #this next section is for the machine 'console'
        main_content_frame.update_idletasks()
        main_Canvas.config(scrollregion=main_Canvas.bbox("all")) 

        self.machine_name = tk.Label(self.frame, text = "Machine ID", font=("Arial Bold",16))
        self.machine_name.grid(row=8, column=2, columnspan=2, sticky="w")

        machine_Canvas = tk.Canvas(self.frame)
        machine_Canvas.grid(row=9, column=2, rowspan=1, columnspan=9, sticky="ew")

        machine_content_frame = tk.Frame(machine_Canvas)
        machine_Canvas.create_window((0, 0), window=machine_content_frame)

        self.populate_bottom_scrollwindow(machine_content_frame)

        y_scrollbar = tk.Scrollbar(self.frame, orient="vertical", command=machine_Canvas.yview)
        y_scrollbar.grid(row=9, column=11, rowspan=1, sticky="ns")
        machine_Canvas.configure(yscrollcommand=y_scrollbar.set)

        x_scrollbar = tk.Scrollbar(self.frame, orient="horizontal", command=machine_Canvas.xview)
        x_scrollbar.grid(row=10, column=2, columnspan=8, sticky="ew")
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
            self.main_details.append(name)
            self.main_details.append(num_computers)
            self.main_details.append(program)
            self.main_details.append(status)

            for f in file:
                split = f[:-1].split('|')
                machine = {"NAME": split[0], "IP": split[1], "CONTENTS": split[2]}
                self.machine_details.append(machine)

    def populate_top_scrollwindow(self, frame):
        data_frame = tk.Frame(frame)
        data_frame.grid(row=0, column=0, sticky="nsew")

        data_label = tk.Label(data_frame, text=str("-"*125), bg="lightblue")
        data_label.grid(row=0, column=0, sticky="nsew")

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
        data_frame = tk.Frame(frame)
        data_frame.grid(row=0, column=0, sticky="nsew")

        data_label = tk.Label(data_frame, text=str("-"*125), bg="lightblue")
        data_label.grid(row=0, column=0, sticky="nsew")
        
        self.machine_text = tk.Label(data_frame, text="", font=("Arial Bold",12))
        self.machine_text.grid(row=1, column=0, sticky="w")

    def inspect_button_clicked(self, name, contents):

        self.machine_text["text"] = contents
        self.machine_name["text"] = f"Machine: {name}"


    def exportdata_button_clicked(self):
        print(f"Export data")
    
    def remove_page(self):
        for widget in self.frame.winfo_children():
            widget.destroy()