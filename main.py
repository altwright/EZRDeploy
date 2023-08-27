from pypsexec.client import Client
from ms_active_directory import ADDomain

if __name__ == "__main__":
    # Create a session object from the current Active Directory Domain
    # TODO: Change to user input login details
    domain = ADDomain(domain="domain.local")
    session = domain.create_session_as_user(user="admin", password="password")
    
    # Compile list of all computers on the domain
    computers = session.find_computers_by_attribute(attribute_name="Enabled", attribute_value="*")
    
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