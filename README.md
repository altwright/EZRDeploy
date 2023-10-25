# EZRDeploy

A network administration tool for managing remote processes on, and copying arbitrary files, to Active Directory domain-joined Windows systems from an Administrator Active Directory user account.
Implemented primarily using the [pypsexec](https://github.com/jborean93/pypsexec) for the backend and [Tk](https://docs.python.org/3/library/tkinter.html)
for the frontend.

The tool was developed as part of a semester-long University of Western Australia project for the unit CITS3200 Professional Computing in semester 2 of 2023.

## Primary Developers

- Benjamin Wright
- Cameron Lee

## Build Instructions

Will only build on Windows systems.

In the root directory install the Python dependencies within a virtual environment:

```sh
pip install -r requirements.txt
```

Then, build the statically-linked executable using [PyInstaller](https://pyinstaller.org/en/stable/):

```sh
pyinstaller -F .\main.py
```
