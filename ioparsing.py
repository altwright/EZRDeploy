from job import Job
from pypsexec.client import Client
from typing import List
            
class Task:
    def __init__(self) -> None:
        self.job: Job
        self.computers: List[Client] = []
        self.author: str
        self.name: str
        self.jobs: list[Job] = []
    
    def run_jobs(self):
        # run the jobs
        for computer in self.computers:
            # convert computer name into client object
            new_job = self.job
            new_job.client = computer # to be converted to client object
            self.jobs.append(new_job)
        
        for job in self.jobs:
            job.run()
        
        return self.jobs
    
    def kill_jobs(self):
        # kill the jobs
        for job in self.jobs:
            job.kill() # replace with actual kill function
            # todo: check if kill successful, if yes then pop, if not error?
        
        self.jobs = []
    
    def kill_specific_job(self, computer):
        # kill a specific job, returns True if successful, False if not
        for job in self.jobs:
            if (job.client == computer):
                job.kill() # replace with actual kill function
                self.jobs.remove(job)
                return True
        return False
    
    def send_specific_input(self, computer, input):
        # take computer and send input using pypsexec, returns True if successful, False if not
        for job in self.jobs:
            if (job.client == computer):
                # send input through stdin
                # put, get, and isEmpty
                return True
        return False

            

class TaskPage:
    def __init__(self, task):
        self.task = task
    
    def restart_all(self):
        # kill all the jobs
        self.task.kill_jobs()
        
        #re run all the jobs
        self.task.run_jobs()
    
    def cancel_all(self):
        # kill all the jobs
        self.task.kill_jobs()
    
    def send_input_to_computer(self, computer, input):
        # take computer and send input using pypsexec
        self.task.send_specific_input(computer, input)
        
    def export_data():
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