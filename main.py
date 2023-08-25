from pypsexec.client import Client

if __name__ == "__main__":
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