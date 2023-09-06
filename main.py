from pypsexec.client import Client 
from win32api import GetComputerNameEx, GetComputerName
from win32con import ComputerNameDnsDomain
from ms_active_directory import ADDomain
from smbprotocol.exceptions import SMBResponseException, NtStatus
from queue import Queue
import threading
import sys

from tasks.execute import execute_job

class AppState:
    computers = [] 

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
    outFileQ = Queue()
    #stdout, stderr, rc = execute_job(client=c, executable="cmd.exe", timeout_seconds=5, stdoutQ=stdoutQ, stderrQ=stderrQ, stdinQ=stdinQ, outFileQ=outFileQ)
    
    job_thread = threading.Thread(target=execute_job, kwargs={"client":c, "executable":"cmd.exe", "timeout_seconds":10, "stdoutQ":stdoutQ, "stderrQ":stderrQ, "stdinQ":stdinQ, "outFileQ":outFileQ})
    job_thread.start()

    for line in sys.stdin:
        if job_thread.is_alive():
            stdinQ.put(line)
        else:
            break

    job_thread.join()

    print('\nSTDOUT:')
    while not stdoutQ.empty():
        print(stdoutQ.get().decode('utf-8'), end="")

    try:
        c.remove_service()
    except SMBResponseException as exc:
        if exc.status != NtStatus.STATUS_CANNOT_DELETE:
            raise exc

    c.disconnect()