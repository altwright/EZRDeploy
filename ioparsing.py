from job import Job

""" class Task:
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
            pass """
            
class Task:
    def __init__(self) -> None:
        self.job: Job
        self.computers: str = []
        self.author: str
        self.name: str
    
    def run_jobs(self):
        # initialise array of jobs
        jobs: Job = []
        
        # run the jobs
        for computer in self.computers:
            # convert computer name into client object
            new_job = self.job
            new_job.client = computer # to be converted to client object
            jobs.append(new_job)
        
        for job in jobs:
            job.run()
        
        return jobs
    
    

class JobPage:
    def __init__(self, job, computers):
        self.job: Job = job
        self.computers = computers
    
    def restart(self):
        # take the job and computers and restart the job
        for computer in self.computers:
            self.job.send_to_machine(computer)
        pass
    
    def cancel(self):
        # take the job and computers and cancel the job
        for computer in self.computers:
            self.job.send_to_machine(computer, "cancel job to do")
        pass
    
    def send_input(self, computer, input):
        # take computer and send input using pypsexec
        self.job.send_to_machine(computer, input)
        pass

class JobCreationPage:
    def __init__(self):
        self.task = Task()
        self.job = Job() # details to be filled once create_job called
    
    def create_job_callback(self, results: dict):
        # create the task
        self.task.author = results["AUTHOR"]
        self.task.name = results["NAME"]
        self.task.computers = results["PCs"]
        
        self.job = Job(executable=results["PROGRAM"], 
                       arguments=results["ARGUMENTS"], 
                       use_system_account=results["SYSADMIN"], 
                       copy_local_exe=results["LOCALMACHINE"], 
                       src_files_list=results["ADDFILES"])
        
        self.task.job = self.job
        
        # run the jobs
        active_task = self.task.run_jobs()