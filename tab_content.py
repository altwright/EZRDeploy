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
    
    def print_selection(self):
        if self.AllMachines.get():
            print("User is choosing all the machines")
        else:
            print("User is not choosing all the machines")

    def open_input_window(self):
        input_window = tk.Toplevel(self)
        input_window.title("Input Information")
        
        # Set the size and position of the popup window
        input_window.geometry('400x300+{}+{}'.format(self.winfo_x() + 50, self.winfo_y() + 50))
        
        pc_label = tk.Label(input_window, text="PC:")
        pc_label.pack()
        pc_entry = tk.Entry(input_window)
        pc_entry.pack()

        avg_label = tk.Label(input_window, text="AVG:")
        avg_label.pack()
        avg_entry = tk.Entry(input_window)
        avg_entry.pack()

        name_label = tk.Label(input_window, text="Name:")
        name_label.pack()
        name_entry = tk.Entry(input_window)
        name_entry.pack()

        description_label = tk.Label(input_window, text="Description:")
        description_label.pack()
        description_entry = tk.Entry(input_window)
        description_entry.pack()

        on_machine_label = tk.Label(input_window, text="On Machine:")
        on_machine_label.pack()
        on_machine_entry = tk.Entry(input_window)
        on_machine_entry.pack()

        filename_label = tk.Label(input_window, text="Filename:")
        filename_label.pack()
        filename_entry = tk.Entry(input_window)
        filename_entry.pack()

        def save_info():
            pc_info = pc_entry.get()
            avg_info = avg_entry.get()
            name_info = name_entry.get()
            description_info = description_entry.get()
            on_machine_info = on_machine_entry.get()
            filename_info = filename_entry.get()

            # Save the information entered by the user or perform other operations
            print("PC:", pc_info)
            print("AVG:", avg_info)
            print("Name:", name_info)
            print("Description:", description_info)
            print("On Machine:", on_machine_info)
            print("Filename:", filename_info)

            # Close the input window after saving
            input_window.destroy()

        save_button = tk.Button(input_window, text="Save", command=save_info)
        save_button.pack()
    


    def create_page(self):
        title = tk.Label(self.frame, text = "Active Directory", bg="lightblue")
        title.grid(row=0, column=5, columnspan=3)

        #checkbox button for selecting all machines listed
        self.AllMachines = tk.BooleanVar()
        select_all_button = ttk.Checkbutton(self.frame, text="Select All Machines", variable=self.AllMachines, onvalue=True, offvalue=False, command=self.print_selection)
        select_all_button.grid(row=1, column=7)

        create_job = ttk.Button(self.frame, text="Create New Job")
        create_job.grid(row=1, column=9, columnspan=1)
        
        # Create a Canvas widget for scrollable content
        canvas = tk.Canvas(self.frame)
        canvas.grid(row=2, column=2, rowspan=8, columnspan=8, sticky="nsew")

        # Create a Frame to contain the actual content
        content_frame = tk.Frame(canvas)
        canvas.create_window((0, 0), window=content_frame, anchor="nw")

 
         
        pc_image1 = Image.open("desktop-outline.png")
        pc_image2 = Image.open("add.png")

        pc_img1 = ImageTk.PhotoImage(resize_image(pc_image1, 100, 100))
        pc_img2 = ImageTk.PhotoImage(resize_image(pc_image2, 30, 30))
        # Define constants for layout
        num_per_row = 5
        spacing = 25  # Adjust as needed

        for i in range(30):
            pc_btn = tk.Button(content_frame, image=pc_img1, width=100, height=100)
            
            # Calculate row and column based on index
            row = (i // num_per_row)*2
            col = i % num_per_row
            

            
            pc_btn.grid(row=row, column=col, padx=spacing, pady=spacing)
            label = tk.Label(content_frame, text=f"PC {i+1}")
            label.grid(row=row+1, column=col, padx=spacing, pady=spacing)

        
        


        # Add scrollbars
        y_scrollbar = tk.Scrollbar(self.frame, orient="vertical", command=canvas.yview)
        y_scrollbar.grid(row=2, column=10, rowspan=8, sticky="ns")
        canvas.configure(yscrollcommand=y_scrollbar.set)



        # Configure mouse wheel scrolling
        def on_mousewheel(event):
            canvas.yview_scroll(-1 * (event.delta // 120), "units")
        canvas.bind_all("<MouseWheel>", on_mousewheel)

        # Update scrollable region
        content_frame.update_idletasks()
        canvas.config(scrollregion=canvas.bbox("all"))    
     
        # Create a button and set the scaled image as the button's image
        btn_right = tk.Button(self.frame, image=pc_img2, width=30, height=30, command=self.open_input_window)
         # Use absolute position to display the button to the right
        btn_right.grid(row=1, column=11)
        
        save_button.pack()

                
    def remove_page(self):
        for widget in self.frame.winfo_children():
            widget.destroy()

class PJTab(tk.Frame):
    def __init__(self, contentFrame, master=None):
        super().__init__(master)
        self.frame = contentFrame
        create_grid(self.frame, 12, 12)

    def create_page(self):
        self.Testing = tk.Label(self.frame, text = "WORKING2!!!")
        self.Testing.grid(row=0, column=1, rowspan=1, sticky="nsew")
            
    def remove_page(self):
        for widget in self.frame.winfo_children():
            widget.destroy()


class JCTab(tk.Frame):
    def __init__(self, contentFrame, master=None):
        super().__init__(master)
        self.frame = contentFrame
        create_grid(self.frame, 12, 12)

    def create_page(self):
        self.Testing = tk.Label(self.frame, text = "WORKING3!!!")
        self.Testing.grid(row=0, column=2, rowspan=1, sticky="nsew")
            
    def remove_page(self):
        for widget in self.frame.winfo_children():
            widget.destroy()



        



        