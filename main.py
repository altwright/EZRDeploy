from pypsexec.client import Client 
from pypsexec.pipe import OutputPipe
from win32api import GetComputerNameEx, GetComputerName
from win32con import ComputerNameDnsDomain
from ms_active_directory import ADDomain
from collections.abc import Generator
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

    stdout, stderr, rc = execute_job(client=c, executable="cmd.exe", arguments="/c echo Hello World")
    
    print('\nSTDOUT:')
    print(stdout.decode('utf-8'))

    c.remove_service()
    c.disconnect()