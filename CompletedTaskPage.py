from tkinter import *
from tkinter import ttk
from tkinter import simpledialog
from tkinter import scrolledtext
from PIL import Image, ImageTk  # Import the PIL library
import tkinter as tk

def resize_image(image, width, height):
    # Use Pillow to scale the image
    resized_image = image.resize((width, height), Image.ANTIALIAS)
    return ImageTk.PhotoImage(resized_image)

def show_page(page):
    # hide all pages
    page1_frame.pack_forget()
    page2_frame.pack_forget()
    page3_frame.pack_forget()

    # Display the corresponding page according to the button click
    if page == "AD":
        page1_frame.pack(fill="both", expand=True) 
        # Change the background color of the button
        btn1.configure(bg="#FFF8DC")
        btn2.configure(bg="lightblue")
        btn3.configure(bg="lightblue")

    elif page == "PJ":
        page2_frame.pack(fill="both", expand=True) 
        # Change the background color of the button
        btn1.configure(bg="lightblue")
        btn2.configure(bg="#FFF8DC")
        btn3.configure(bg="lightblue")

    elif page == "JC":
        page3_frame.pack(fill="both", expand=True) 
        # Change the background color of the button
        btn1.configure(bg="lightblue")
        btn2.configure(bg="lightblue")
        btn3.configure(bg="#FFF8DC")


root = Tk()
root.title("All Code")  # Window title
height = 600
width = 1200
root.geometry('1200x600')  # Window size
root.minsize(width, height)  # Set the minimum window size
root.maxsize(width, height)  # Set the maximum window size

# Create a Frame for the left button
left_frame = Frame(root)
left_frame.grid(column=0, row=0, padx=10, pady=10)

btn1 = Button(left_frame, text="AD", font=("Arial Bold", 30), command=lambda: show_page("AD"))
btn1.grid(column=0, row=0, pady=10)
btn2 = Button(left_frame, text="PJ", font=("Arial Bold", 30), command=lambda: show_page("PJ"))
btn2.grid(column=0, row=1, pady=10)
btn3 = Button(left_frame, text="JC", font=("Arial Bold", 30), command=lambda: show_page("JC"))
btn3.grid(column=0, row=2, pady=10)


# Initially set the background color of the "AD" button to dark
btn1.configure(bg="#FFF8DC")
btn2.configure(bg="lightblue")
btn3.configure(bg="lightblue")

# Separator between button and content
separator = ttk.Separator(root, orient="vertical")
separator.grid(column=1, row=0, rowspan=3, sticky='nsew', padx=10)

#Create a Frame for the content on the right
right_frame = Frame(root)
right_frame.grid(column=2, row=0, sticky="nsew")  # Use the sticky parameter to make the right Frame fill the entire second column and subsequent columns
# Use columnconfigure to set the weight of column 2 and beyond to ensure that right_frame fills the entire column
root.grid_columnconfigure(0, weight=1)  # Set the weight of the left Frame column to 1
root.grid_rowconfigure(0, weight=1)  #Set the weight of row 0 to 1 to ensure that the content on the left and right sides occupies the entire height of the window
root.grid_columnconfigure(2, weight=18)

# Create three different pages, each containing different controls
page1_frame = Frame(right_frame)
page1_frame.pack(fill="both", expand=True)

connected = Label(page1_frame, text="· connected",fg='green', font=("Arial Bold",12))
connected.place(relx=0.5, rely=0.1, anchor="center") 

# Load the image and set it as the button's image
image = Image.open("add.png")  # Replace with the converted image file path
#Set the scaled image width and height
scaled_width = 30
scaled_height = 30
# Call the function to scale the image
tk_image = resize_image(image, scaled_width, scaled_height)
# Create a button and set the scaled image as the button's image
btn_right = Button(page1_frame, image=tk_image, width=scaled_width, height=scaled_height)
btn_right.place(x=900, y=10)   # Use absolute position to display buttons to the right
image2 = Image.open("alert-outline.png")  # Replace with the converted image file path
scaled_width = 30
scaled_height = 30
tk_image2 = resize_image(image2, scaled_width, scaled_height)
btn_right2 = Button(page1_frame, image=tk_image2, width=scaled_width, height=scaled_height)
btn_right2.place(x=950, y=10)   

pc1 = Image.open("desktop-outline.png")  # Replace with the converted image file path
scaled_width = 100
scaled_height = 100
pc1_img = resize_image(pc1, scaled_width, scaled_height)
pc1_btn = Button(page1_frame, image=pc1_img, width=scaled_width, height=scaled_height)
pc1_btn.place(x=250, y=100)   

pc2_btn = Button(page1_frame, image=pc1_img, width=scaled_width, height=scaled_height)
pc2_btn.place(x=370, y=100)   

pc3_btn = Button(page1_frame, image=pc1_img, width=scaled_width, height=scaled_height)
pc3_btn.place(x=490, y=100)   

pc4_btn = Button(page1_frame, image=pc1_img, width=scaled_width, height=scaled_height)
pc4_btn.place(x=620, y=100)   

pc5_btn = Button(page1_frame, image=pc1_img, width=scaled_width, height=scaled_height)
pc5_btn.place(x=740, y=100)   


page2_frame = Frame(right_frame)
page2_frame.pack(fill="both", expand=True)
# label2 = Label(page2_frame, text="This is the PJ page", font=("Arial Bold", 20))
# label2.pack(fill="both", expand=True,)

search_label = Entry(page2_frame, width=30)
search_label.insert(0, "输入搜索内容")  # insert default text
search_label.place(x=80, y=100)

search_label2 = Entry(page2_frame, width=30)
search_label2.insert(0, "输入搜索内容")  # insert default text
search_label2.place(x=580, y=100)

text_label = Text(page2_frame,width=40, height=30)
text_label.place(x=80, y=180)
def on_entry_change(event):
    text = search_label.get()  # Get the text in Entry
    
    text_label.delete(1.0, END)  # Clear the text in the Text component
    text_label.insert(END, text)  #Insert new text in the Text component
search_label.bind("<Return>",on_entry_change)
text_label3 = Text(page2_frame ,width=40, height=30)
text_label3.place(x=580, y=180)


#  page-Competed
def inspect_button_clicked(row_number):
    print(f"Inspect button clicked for row {row_number}")
    # Clear the previous text content
    text_terminal.delete(1.0, tk.END)
    # Output machine and ID to Text_terminal
    text_terminal.insert(tk.END, f"Machine: {row_number}, ID: {row_number}\n")
    text_terminal.see(tk.END)  # scroll Text_terminal to the last line
def exportdata_button_clicked():
    print(f"Export data")
page3_frame = Frame(right_frame)
page3_frame.pack(fill="both", expand=True)
label3 = Label(page3_frame, text="Task1", font=("Arial Bold", 20))
connected = Label(page3_frame, text="· Competed",fg='green', font=("Arial Bold",12))
connected.place(relx=0.1, rely=0.1, anchor="center")    
label_task = Label(page3_frame, text="Task Name:"+label3.cget("text"), font=("Arial Bold", 20))
label_task.place(x=80, y=80)
label_time = Label(page3_frame, text="2023:08:27", font=("Arial Bold", 15))
label_time.place(x=80, y=120)
btn_cancel = Button(page3_frame, text="Export task data", font=("Arial Bold", 12),command=exportdata_button_clicked)
btn_cancel.place(x=580, y=80)
table_frame = Frame(page3_frame)
table_frame.place(x=80, y=180)
# Create Canvas
canvas = tk.Canvas(table_frame)
canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
# Create the Frame in the table
table = ttk.Frame(canvas, borderwidth=1, relief="solid")
canvas.create_window((0, 0), window=table, anchor="nw")
# Add sample data and buttons
row_count = 50  # Specify the number of rows
for i in range(1, row_count + 1):
    row_frame = ttk.Frame(table)
    row_frame.grid(row=i, column=0, sticky="w", padx=10, pady=5)

    label1 = tk.Label(row_frame, text=f'Machine-{i}')
    label1.grid(row=0, column=0, padx=10)

    label2 = tk.Label(row_frame, text=f'ID-{i}')
    label2.grid(row=0, column=1, padx=50)

    inspect_button = tk.Button(row_frame, text='Inspect', command=lambda row=i: inspect_button_clicked(row))
    inspect_button.grid(row=0, column=2, padx=50)

    separator_bottom = ttk.Separator(row_frame, orient="horizontal")
    separator_bottom.grid(row=1, column=0, columnspan=3, sticky="ew")
# Add an extra empty row below the last row in the table
empty_row_frame = ttk.Frame(table)
empty_row_frame.grid(row=row_count + 1, column=0, sticky="w", padx=10, pady=5)
# Add the top border of the table
table_top_separator = ttk.Separator(table, orient="horizontal")
table_top_separator.grid(row=0, column=0, columnspan=3, sticky="ew")
#Add the left border of the table
table_left_separator = ttk.Separator(table, orient="vertical")
table_left_separator.grid(row=0, column=0, rowspan=row_count + 2, sticky="ns")
#Create the Frame of the scroll bar
scrollbar_frame = ttk.Frame(table_frame)
scrollbar_frame.pack(side=tk.RIGHT, fill=tk.Y)
#Create scroll bar
scrollbar = ttk.Scrollbar(scrollbar_frame, orient=tk.VERTICAL, command=canvas.yview)
scrollbar.pack(fill=tk.Y, expand=True)
#Configure the scrolling area of the Canvas
canvas.configure(yscrollcommand=scrollbar.set)
canvas.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
#Add the right border of the table
table_right_separator = ttk.Separator(table_frame, orient="vertical")
table_right_separator.pack(side=tk.RIGHT, fill=tk.Y)

label_terminal = Label(page3_frame, text="Machine ID", font=("Arial Bold", 20))
label_terminal.place(x=80, y=450)
text_terminal = Text(page3_frame,width=100, height=8)
text_terminal.place(x=80, y=500)

show_page("JC")
root.mainloop()
