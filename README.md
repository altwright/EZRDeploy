# EZRDeploy

A network administration tool for managing remote processes on, and copying arbitrary files, to Active Directory domain-joined Windows systems from an Administrator Active Directory user account.
Implemented primarily using [pypsexec](https://github.com/jborean93/pypsexec) for the backend and [Tk](https://docs.python.org/3/library/tkinter.html)
for the frontend.

The tool was developed as part of a semester-long University of Western Australia project for the unit CITS3200 Professional Computing in semester 2 of 2023.

## Lead Developers

- [Benjamin Wright](https://github.com/altwright): backend development
- [Cameron Lee](https://github.com/CameronLee02): frontend developemt

## Build Instructions

Will only build on Windows systems. It has only been tested to work within the [Windows 11 Lab Deployment Kit](https://info.microsoft.com/ww-landing-windows-11-office-365-lab-kit.html) from the Domain Controller VM.

In the root directory install the Python dependencies within a virtual environment:

```sh
pip install -r requirements.txt
```

Then, build the statically-linked executable using [PyInstaller](https://pyinstaller.org/en/stable/):

```sh
pyinstaller -F .\main.py
```

## Sceenshots

**Active Directory** screen, for remote systems selection.

![Pasted image](https://github.com/altwright/ezrdeploy/assets/110673989/16972ff5-8c27-49bc-84ef-bed51fdb2bc6)

**Job Configuration** screen.

![Pasted image 1](https://github.com/altwright/ezrdeploy/assets/110673989/50e30f7a-47db-4933-b2a0-e3217ca848aa)

**Running Job** screen, where individual remote systems can be inspected and all the remote processes can be managed asynchronously.

![Pasted image 2](https://github.com/altwright/ezrdeploy/assets/110673989/7acaffc5-b5aa-46e5-bd10-f56adb7028ea)

Features a **real-time console** that prints the standard output and accepts standard input for a remote process.

![Pasted image 3](https://github.com/altwright/ezrdeploy/assets/110673989/5da814d5-48c9-4240-a293-77ad9434e84e)
