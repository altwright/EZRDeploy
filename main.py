from pypsexec.client import Client 
from win32api import GetComputerNameEx, GetComputerName
from win32con import ComputerNameDnsDomain
from ms_active_directory import ADDomain, ADGroup
from UI import uiMain
from job import Job
from appstate import appState

if __name__ == "__main__":
    appState.domainName = GetComputerNameEx(ComputerNameDnsDomain)
    appState.hostComputer = GetComputerName()

    aDDomain = ADDomain(appState.domainName)
    appState.aDSession = aDDomain.create_session_as_computer(appState.hostComputer)

    uiMain()