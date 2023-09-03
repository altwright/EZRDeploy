class Task:
    def __init__(self, name=None, desc=None, on_machine=False, file=None, file_name=None, args=None):
        self.name = name
        self.desc = desc
        self.on_machine = on_machine
        self.file = file
        self.file_name = file_name
        self.args = args
    
    # functions to append details to the task, maybe when wanting to edit task?
    def add_name(self, name):
        self.name = name
    
    def add_desc(self, desc):
        self.desc = desc
    
    def add_on_machine(self, on_machine):
        self.on_machine = on_machine
        
    def add_file(self, file): # only if on_machine is false
        if (not self.on_machine):
            self.file = file
        else:
            print("Cannot add file if on_machine is true")
    
    def add_file_name(self, file_name): # only if on_machine is true
        if (self.on_machine):
            self.file_name = file_name
    
    def add_args(self, args):
        self.args = args
    
    def send_to_machine(self, computer, input=None):
        # send the task to the computer
        if (not input):
            # call pypsexec here to send task to machine
            pass
        else:
            # call pypsexec here to send whatever input to the machine
            pass

class TaskPage:
    def __init__(self, task, computers):
        self.task = task
        self.computers = computers
    
    def restart(self):
        # take the task and computers and restart the task
        for computer in self.computers:
            self.task.send_to_machine(computer)
        pass
    
    def cancel(self):
        # take the task and computers and cancel the task
        for computer in self.computers:
            self.task.send_to_machine(computer, "cancel task to do")
        pass
    
    def send_input(self, computer, input):
        # take computer and send input using pypsexec
        self.task.send_to_machine(computer, input)
        pass

class TaskCreationPage:
    def __init__(self):
        self.task = Task() # details to be filled once create_task called
    
    def create_task(self):
        # create the task
        self.task.add_name(name.get()) # get name from tkinter, name is placeholder
        pass