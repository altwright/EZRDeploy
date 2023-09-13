from pypsexec.client import Client 
from win32api import GetComputerNameEx, GetComputerName
from win32con import ComputerNameDnsDomain
from ms_active_directory import ADDomain
from smbprotocol.exceptions import SMBResponseException, NtStatus
from queue import Queue
import threading
import sys

from job import Job

class AppState:
    computers = [] 

def print_stdout(stdoutQ: Queue):
    while True:
        if not stdoutQ.empty():
            print(stdoutQ.get(), end="")

def get_stdin(stdinQ: Queue, cancel_event: threading.Event):
    for line in sys.stdin:
        if line.find("\CANCEL"):
            stdinQ.put(line)
        else:
            cancel_event.set()

if __name__ == "__main__":
    domainName = GetComputerNameEx(ComputerNameDnsDomain)
    print("DOMAIN: " + domainName)

    hostComputer = GetComputerName()
    print("HOST COMPUTER: " + hostComputer)

    domain = ADDomain(domainName)
    session = domain.create_session_as_computer(hostComputer)
    computers = session.find_computers_by_common_name("*", ['operatingSystem', 'operatingSystemVersion'])

    print("DOMAIN-JOINED COMPUTERS: ")
    for computer in computers:
        if computer.name != hostComputer:
            print('\t' + computer.name)
            AppState.computers.append(computer)

    c = Client("CLIENT1")
    c.connect()
    c.create_service()

    stdoutQ = Queue()
    stderrQ = Queue()
    stdinQ = Queue()
    cancel_event = threading.Event()
    
    job = Job(c, "cmd.exe", None, stdoutQ, stderrQ, stdinQ, 
              timeout_seconds=60, 
              copy_local_exe=False, 
              local_exe_src_dir=".\\dist", 
              overwrite_remote_exe=True,
              working_dir=r'C:\Users\Administrator\Desktop',
              copy_local_files=False,
              src_files_list=[r".\dist\test.txt"],
              overwrite_remote_files=True,
              clean_copied_files_after=True,
              clean_copied_exe_after=True,
              use_system_account=True
              )
    job.start()

    print('\nSTDOUT:')
    stdout_thread = threading.Thread(target=print_stdout, args=(stdoutQ,), daemon=True)
    stderr_thread = threading.Thread(target=print_stdout, args=(stderrQ,), daemon=True)
    stdin_thread = threading.Thread(target=get_stdin, args=(stdinQ, cancel_event), daemon=True)
    stdout_thread.start()
    stderr_thread.start()
    stdin_thread.start()

    job.join()

    print('\nRETURN CODE: ' + str(job.rc))
    try:
        c.cleanup()
    except SMBResponseException as exc:
        if exc.status != NtStatus.STATUS_CANNOT_DELETE:
            raise exc
        else:
            print("Failed to delete service!")

    c.disconnect()