class Job:
    def __init__(self, name=None, desc=None, on_machine=False, file=None, file_name=None, args=None):
        self.name = name
        self.desc = desc
        self.on_machine = on_machine
        self.file = file
        self.file_name = file_name
        self.args = args
    
    # functions to append details to the job, maybe when wanting to edit job?
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

class TaskPage:
    def __init__(self, job, computers):
        self.job = job
        self.computers = computers
        pass
    
    def restart(self):
        # take the job and computers and restart the job
        pass
    
    def cancel(self):
        # take the job and computers and cancel the job
        pass
    
    def send_input(self, input):
        # take computer and send input using pypsexec
        pass