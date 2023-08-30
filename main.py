from pypsexec.client import Client
from win32api import GetComputerNameEx, GetComputerName
from win32con import ComputerNameDnsDomain
from ms_active_directory import ADDomain


if __name__ == "__main__":
    domainName = GetComputerNameEx(ComputerNameDnsDomain)
    print("DOMAIN: " + domainName)

    computerName = GetComputerName()
    print("COMPUTER: " + computerName)

    domain = ADDomain(domainName)
    session = domain.create_session_as_computer(computerName)
    computers = session.find_computers_by_common_name("*")
    print("DOMAIN-JOINED COMPUTERS: ")
    for computer in computers:
        print(computer.common_name)

    c = Client("CLIENT1")
    c.connect()
    try:
        c.create_service()

        # After creating the service, you can run multiple exe's without
        # reconnecting

        # run a simple cmd.exe program with arguments
        stdout, stderr, rc = c.run_executable("cmd.exe", arguments="/c echo Hello World")
        print("STDOUT: " + stdout.decode('utf-8'))
        print("STDERR: " + stderr.decode('utf-8'))
    finally:
        c.remove_service()
        c.disconnect()