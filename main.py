from pypsexec.client import Client 
from win32api import GetComputerNameEx, GetComputerName
from win32con import ComputerNameDnsDomain
from ms_active_directory import ADDomain
from smbprotocol.exceptions import SMBResponseException, NtStatus
from queue import Queue
import threading
import sys

from tasks.execution import JobThread

class AppState:
    computers = [] 

def print_stdout(stdoutQ: Queue):
    while True:
        if not stdoutQ.empty():
            print(stdoutQ.get(), end="")

def get_stdin(stdinQ: Queue):
    for line in sys.stdin:
        stdinQ.put(line)

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

    c = Client("CLIENT2")
    c.connect()
    c.create_service()

    stdoutQ = Queue()
    stderrQ = Queue()
    stdinQ = Queue()
    input_finished = threading.Event()
    
    job_thread = JobThread(c, "whoami.exe", None, stdoutQ, stderrQ, stdinQ, timeout_seconds=0, input_finished_event=input_finished)
    job_thread.start()

    print('\nSTDOUT:')
    stdout_thread = threading.Thread(target=print_stdout, args=(stdoutQ,), daemon=True)
    stdin_thread = threading.Thread(target=get_stdin, args=(stdinQ,), daemon=True)
    stdout_thread.start()
    stdin_thread.start()

    job_thread.join()

    try:
        c.remove_service()
    except SMBResponseException as exc:
        if exc.status != NtStatus.STATUS_CANNOT_DELETE:
            raise exc

    c.disconnect()