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
    def __init__(self, contentFrame, master=None):
        super().__init__(master)
        self.frame = contentFrame
        create_grid(self.frame, 12, 12)
        self.pc_buttons = []
        self.chosen_pc = []
    
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
            print("User is not choosing all the machines")
    
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
        title = tk.Label(self.frame, text = "Active Directory", bg="lightblue")
        title.grid(row=0, column=5, columnspan=3)

        #checkbox button for selecting all machines listed
        self.AllMachines = tk.BooleanVar()
        select_all_button = ttk.Checkbutton(self.frame, text="Select All Machines", variable=self.AllMachines, onvalue=True, offvalue=False, command=self.select_all_machines)
        select_all_button.grid(row=1, column=7)

        self.create_job = ttk.Button(self.frame, text="Create New Job", state=tk.DISABLED)
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
    def __init__(self, contentFrame, master=None):
        super().__init__(master)
        self.frame = contentFrame
        create_grid(self.frame, 12, 12)

    def create_page(self):
        # Left side
        search_bar = tk.Entry(self.frame)
        search_bar.insert(0, "Enter search")
        search_bar.grid(row=1, column=1, columnspan=4, sticky="nsew")

        frame1 = tk.Frame(self.frame, bg="blue")
        frame1.grid(row=4, column=1, rowspan=7, columnspan=4, sticky="nsew")

        # Right side
        frame2 = tk.Frame(self.frame, bg="green")
        frame2.grid(row=1, column=7, rowspan=2, columnspan=4, sticky="nsew")

        frame3 = tk.Frame(self.frame, bg="red")
        frame3.grid(row=4, column=7, rowspan=7, columnspan=4, sticky="nsew")

            
    def remove_page(self):
        for widget in self.frame.winfo_children():
            widget.destroy()


class JCTab(tk.Frame):
    def __init__(self, contentFrame, master=None):
        super().__init__(master)
        self.frame = contentFrame
        create_grid(self.frame, 12, 12)

    def create_page(self):
        # Left side
        search_bar = tk.Entry(self.frame)
        search_bar.insert(0, "Enter search")
        search_bar.grid(row=1, column=1, columnspan=4, sticky="nsew")

        frame1 = tk.Frame(self.frame, bg="blue")
        frame1.grid(row=4, column=1, rowspan=7, columnspan=4, sticky="nsew")

        # Right side
        frame2 = tk.Frame(self.frame, bg="green")
        frame2.grid(row=1, column=7, rowspan=2, columnspan=4, sticky="nsew")

        frame3 = tk.Frame(self.frame, bg="red")
        frame3.grid(row=4, column=7, rowspan=7, columnspan=4, sticky="nsew")
            
    def remove_page(self):
        for widget in self.frame.winfo_children():
            widget.destroy()


class active_tab(tk.Frame):
    def __init__(self, contentFrame, master=None):
        super().__init__(master)
        self.frame = contentFrame
        create_grid(self.frame, 12, 12)

    def create_page(self):


        frame1 = tk.Frame(self.frame, bg="blue")
        frame1.grid(row=2, column=2, rowspan=6, columnspan=8, sticky="nsew")

       
        frame2 = tk.Frame(self.frame, bg="green")
        frame2.grid(row=9, column=2, rowspan=2, columnspan=8, sticky="nsew")


            
    def remove_page(self):
        for widget in self.frame.winfo_children():
            widget.destroy()