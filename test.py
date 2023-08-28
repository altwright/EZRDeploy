from tkinter import *
from tkinter import ttk
from tkinter import simpledialog
from tkinter import scrolledtext
from PIL import Image, ImageTk

def open_input_window():
    input_window = Toplevel(root)
    input_window.title("Input Information")
    # Set the size and position of the popup window
    input_window.geometry('400x300+{}+{}'.format(root.winfo_x() + 50, root.winfo_y() + 50))
    pc_label = Label(input_window, text="PC:")
    pc_label.pack()
    pc_entry = Entry(input_window)
    pc_entry.pack()

    avg_label = Label(input_window, text="AVG:")
    avg_label.pack()
    avg_entry = Entry(input_window)
    avg_entry.pack()

    name_label = Label(input_window, text="Name:")
    name_label.pack()
    name_entry = Entry(input_window)
    name_entry.pack()

    description_label = Label(input_window, text="Description:")
    description_label.pack()
    description_entry = Entry(input_window)
    description_entry.pack()

    on_machine_label = Label(input_window, text="On Machine:")
    on_machine_label.pack()
    on_machine_entry = Entry(input_window)
    on_machine_entry.pack()

    filename_label = Label(input_window, text="Filename:")
    filename_label.pack()
    filename_entry = Entry(input_window)
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

    save_button = Button(input_window, text="Save", command=save_info)
    save_button.pack()

def resize_image(image, width, height):
    # Use Pillow to scale images
    resized_image = image.resize((width, height), Image.ANTIALIAS)
    return ImageTk.PhotoImage(resized_image)

def show_page(page):
    # hide all pages
    self.frame.pack_forget()
    page2_frame.pack_forget()
    page3_frame.pack_forget()
    page4_frame.pack_forget()
    page5_frame.pack_forget()

    # Display the corresponding page according to the button click
    if page == "AD":
        self.frame.pack(fill="both", expand=True) 
        # Change the background color of the button
        btn1.configure(bg="#FFF8DC")
        btn2.configure(bg="lightblue")
        btn3.configure(bg="lightblue")
        btn4.configure(bg="lightblue")
        btn5.configure(bg="lightblue")
    elif page == "PJ":
        page2_frame.pack(fill="both", expand=True) 
        # Change the background color of the button
        btn1.configure(bg="lightblue")
        btn2.configure(bg="#FFF8DC")
        btn3.configure(bg="lightblue")
        btn4.configure(bg="lightblue")
        btn5.configure(bg="lightblue")
    elif page == "JC":
        page3_frame.pack(fill="both", expand=True) 
        # Change the background color of the button
        btn1.configure(bg="lightblue")
        btn2.configure(bg="lightblue")
        btn3.configure(bg="#FFF8DC")
        btn4.configure(bg="lightblue")
        btn5.configure(bg="lightblue")
    elif page == "JC1":
        page4_frame.pack(fill="both", expand=True) 
        # Change the background color of the button
        btn1.configure(bg="lightblue")
        btn2.configure(bg="lightblue")
        btn3.configure(bg="lightblue")
        btn4.configure(bg="#FFF8DC")
        btn5.configure(bg="lightblue")
    elif page == "JC2":
        page5_frame.pack(fill="both", expand=True) 
        # Change the background color of the button
        btn1.configure(bg="lightblue")
        btn2.configure(bg="lightblue")
        btn3.configure(bg="lightblue")
        btn4.configure(bg="lightblue")
        btn5.configure(bg="#FFF8DC")

root = Tk()
root.title("All Code")  # window title
height = 600
width = 1200
root.geometry('1200x600')  # window size
root.minsize(width, height)  # set minimum window size
root.maxsize(width, height)  # set the maximum window size
# Create a Frame for the left button
left_frame = Frame(root)
left_frame.grid(column=0, row=0, padx=10, pady=10)

btn1 = Button(left_frame, text="AD", font=("Arial Bold", 30), command=lambda: show_page("AD"))
btn1.grid(column=0, row=0, pady=10)
btn2 = Button(left_frame, text="PJ", font=("Arial Bold", 30), command=lambda: show_page("PJ"))
btn2.grid(column=0, row=1, pady=10)
btn3 = Button(left_frame, text="JC", font=("Arial Bold", 30), command=lambda: show_page("JC"))
btn3.grid(column=0, row=2, pady=10)
btn4 = Button(left_frame, text="JC1", font=("Arial Bold", 25), command=lambda: show_page("JC1"))
btn4.grid(column=0, row=3, pady=6)
btn5 = Button(left_frame, text="JC2", font=("Arial Bold", 25), command=lambda: show_page("JC2"))
btn5.grid(column=0, row=4, pady=6)

# Initially set the background color of the "AD" button to a dark color
btn1.configure(bg="#FFF8DC")
btn2.configure(bg="lightblue")
btn3.configure(bg="lightblue")
btn4.configure(bg="lightblue")
btn5.configure(bg="lightblue")

# Divider between button and content
separator = ttk.Separator(root, orient="vertical")
separator.grid(column=1, row=0, rowspan=3, sticky='nsew', padx=10)

# Create a Frame for right content
right_frame = Frame(root)
right_frame.grid(column=2, row=0, sticky="nsew")  # Use the sticky parameter to make the right Frame fill the entire column 2 and beyond
# Use columnconfigure to set the weight of column 2 and beyond to ensure right_frame fills the entire column
root.grid_columnconfigure(0, weight=1) # Set the weight of the left Frame column to 1
root.grid_rowconfigure(0, weight=1)  # Set the weight of line 0 to 1 to ensure that the content on the left and right sides occupies the entire height of the window
root.grid_columnconfigure(2, weight=18)

# Create three different pages, each containing different controls
self.frame = Frame(right_frame)
self.frame.pack(fill="both", expand=True)

connected = Label(self.frame, text="· connected",fg='green', font=("Arial Bold",12))
connected.place(relx=0.5, rely=0.1, anchor="center") 

# Load the image and set it as the button's image
image = Image.open("add.png")  # Replace with converted image file path
# Set the scaled image width and height
scaled_width = 30
scaled_height = 30
# Call the function to scale the image
tk_image = resize_image(image, scaled_width, scaled_height)
# Create a button and set the scaled image as the button's image
btn_right = Button(self.frame, image=tk_image, width=scaled_width, height=scaled_height, command=open_input_window)
btn_right.place(x=900, y=10)   # Use absolute position to display the button to the right

image2 = Image.open("alert-outline.png")  # Replace with converted image file path
scaled_width = 30
scaled_height = 30
tk_image2 = resize_image(image2, scaled_width, scaled_height)
btn_right2 = Button(self.frame, image=tk_image2, width=scaled_width, height=scaled_height)
btn_right2.place(x=950, y=10)   

pc1 = Image.open("desktop-outline.png")  # Replace with converted image file path
scaled_width = 100
scaled_height = 100
pc1_img = resize_image(pc1, scaled_width, scaled_height)
pc1_btn = Button(self.frame, image=pc1_img, width=scaled_width, height=scaled_height)
pc1_btn.place(x=250, y=100)   

pc2_btn = Button(self.frame, image=pc1_img, width=scaled_width, height=scaled_height)
pc2_btn.place(x=370, y=100)   

pc3_btn = Button(self.frame, image=pc1_img, width=scaled_width, height=scaled_height)
pc3_btn.place(x=490, y=100)   

pc4_btn = Button(self.frame, image=pc1_img, width=scaled_width, height=scaled_height)
pc4_btn.place(x=620, y=100)   

pc5_btn = Button(self.frame, image=pc1_img, width=scaled_width, height=scaled_height)
pc5_btn.place(x=740, y=100)   


page2_frame = Frame(right_frame)
page2_frame.pack(fill="both", expand=True)


search_label = Entry(page2_frame, width=30)
search_label.insert(0, "enter search")  
search_label.place(x=80, y=100)

search_label2 = Entry(page2_frame, width=30)
search_label2.insert(0, "enter search")  
search_label2.place(x=580, y=100)

text_label = Text(page2_frame,width=40, height=30)
text_label.place(x=80, y=180)
def on_entry_change(event):
    text = search_label.get()  
    text_label.delete(1.0, END) 
    text_label.insert(END, text)
search_label.bind("<Return>",on_entry_change)
text_label3 = Text(page2_frame ,width=40, height=30)
text_label3.place(x=580, y=180)


page3_frame = Frame(right_frame)
page3_frame.pack(fill="both", expand=True)
label3 = Label(page3_frame, text=" JC page", font=("Arial Bold", 20))
label3.pack(fill="both", expand=True,)

page4_frame = Frame(right_frame)
page4_frame.pack(fill="both", expand=True)
label4 = Label(page4_frame, text="JC 1 page", font=("Arial Bold", 20))
# label3.pack(fill="both", expand=True,)

page5_frame = Frame(right_frame)
page5_frame.pack(fill="both", expand=True)
label5 = Label(page5_frame, text="JC 2 page", font=("Arial Bold", 20))
# label3.pack(fill="both", expand=True,)

def task_page(page,label3):
    connected = Label(page, text="· connected",fg='green', font=("Arial Bold",12))
    connected.place(relx=0.1, rely=0.1, anchor="center")    
    label_task = Label(page, text="Task Name:"+label3.cget("text"), font=("Arial Bold", 20))
    label_task.place(x=80, y=80)
    label_time = Label(page, text="2023:08:27", font=("Arial Bold", 15))
    label_time.place(x=80, y=120)
    btn_cancel = Button(page, text="Cancel", font=("Arial Bold", 12))
    btn_cancel.place(x=580, y=80)
    btn_restart = Button(page, text="Restart", font=("Arial Bold", 12))
    btn_restart.place(x=680, y=80)

    
    text_box = scrolledtext.ScrolledText(page, width=50, height=10)
    text_box.place(x=80, y=160,width=700)  # Adjust the position of the text box
    initial_text = "test\ntest\ntest\ntest\ntest\ntest\ntest\ntest\ntest\ntest\n"
    text_box.insert("1.0", initial_text)

    text_box2 = scrolledtext.ScrolledText(page, width=50, height=10)
    text_box2.place(x=80, y=360,width=700)  # Adjust the position of the text box
    text_box2.insert("1.0", initial_text)
task_page(page4_frame,label4)
task_page(page5_frame,label5)


# Show the "AD" page by default at program startup
show_page("AD")
root.mainloop()
