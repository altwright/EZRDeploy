from ms_active_directory.core.ad_objects import ADComputer
from ms_active_directory.core.ad_session import ADSession
from pypsexec.client import Client 
from queue import Queue
from job import Job
from datetime import datetime

class JobState:
    clientName: str
    client: Client
    stdoutQ: Queue
    job: Job
    exc: Exception = None

class TaskState:
    started: bool = False
    name: str
    author: str
    startDateTime: datetime
    programStr: str
    argsStr: str
    localProgram: bool
    localProgramSrcDir: str
    copyFiles: bool
    copiedFilesList: list[str]
    remoteWorkingDir: str
    impersonateSysAdmin: bool
    jobList: list[JobState] = []
    overwriteExe: bool
    overwriteFiles: bool
    cleanupExeAfterCopy: bool
    cleanupFilesAfterCopy: bool
    timeout: int

class AppState:
    domainName: str
    hostComputer: str
    aDSession: ADSession
    runningTasks: list[TaskState] = []
    completedTasks: list[TaskState] = []

appState = AppState()