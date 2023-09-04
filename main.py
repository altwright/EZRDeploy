from pypsexec.client import Client 
from pypsexec.pipe import OutputPipeBytes
from win32api import GetComputerNameEx, GetComputerName
from win32con import ComputerNameDnsDomain
from ms_active_directory import ADDomain
from collections.abc import Generator
import sys

class AppState:
    computers = [] 

def handleInput():
    for line in sys.stdin:
        yield bytes(line, 'utf-8')

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

    stdoutPipe = OutputPipeBytes
    stderrPipe = OutputPipeBytes

    stdout, stderr, rc = c.run_executable("cmd.exe", stdout=stdoutPipe, stderr=stderrPipe, stdin=handleInput, timeout_seconds=10)
    
    print('\nSTDOUT:')
    print(stdout.decode('utf-8'))

    c.remove_service()
    c.disconnect()