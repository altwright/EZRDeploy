from ms_active_directory.core.ad_objects import ADComputer
from ms_active_directory.core.ad_session import ADSession

class AppState:
    domainName: str
    hostComputer: str
    aDSession: ADSession

appState = AppState()