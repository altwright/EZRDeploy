import tkinter as tk
from tkinter import colorchooser

class ADTab(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        chat_label = tk.Label(self, text="Chat Functionality", font=("Helvetica", 20))
        chat_label.pack(pady=20)
        
        self.message_input = tk.Entry(self)  # Use self.message_input
        self.message_input.pack(pady=10)
        
        self.message_display = tk.Text(self, height=10, width=50)  # Use self.message_display
        self.message_display.pack(pady=10)
        
        def send_message():
            message = self.message_input.get()
            self.message_display.insert(tk.END, message + "\n")
            self.message_input.delete(0, tk.END)
            
        send_button = tk.Button(self, text="Send", command=send_message)
        send_button.pack()

class PJTab(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        search_label = tk.Label(self, text="Search Functionality", font=("Helvetica", 20))
        search_label.pack(pady=20)
        
        self.search_entry = tk.Entry(self)  # Use self.search_entry
        self.search_entry.pack(pady=10)
        
        def perform_search():
            search_term = self.search_entry.get()
            # Add search logic here
            self.search_result_label.config(text=f"Search Result for '{search_term}':")
            
        search_button = tk.Button(self, text="Search", command=perform_search)
        search_button.pack()
        
        self.search_result_label = tk.Label(self, text="", font=("Helvetica", 16))  # Use self.search_result_label
        self.search_result_label.pack(pady=10)
        
class CJTab(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        def change_color():
            color = colorchooser.askcolor()[1]
            self.config(bg=color)
            
        color_label = tk.Label(self, text="Change Color Functionality", font=("Helvetica", 20))
        color_label.pack(pady=20)
        
        color_button = tk.Button(self, text="Change Color", command=change_color)
        color_button.pack()
        
        welcome_label = tk.Label(self, text="Welcome to the Color Tab!", font=("Helvetica", 16))
        welcome_label.pack(pady=10)
