# project-3200
Sysadmin software for network deployment of cyberforensics tools using Active Directory and PAExec

## pypsexec_mods Folder
**Replace the files found in the imported pypsexec library with the equivalently named files in this folder.**

## Console
The handle_output function is called whenever there is new standard output from the remote process.
Should this output be continually appended to a new file, or should we wait until the process ends before
writing the full buffer to disk?
We should have an index into the buffer that tracks how much has been read from. The graphical console should
then poll the stdout pipe for new bytes.
The console will pass a string to the stdin.
Stdin needs to be accepted until stdout has signalled that it has finished.
The run_executable method should accept instances of stdout and stdin handler classes. When bytes written
to the stdout handler, they should write them to the graphical console, and when bytes are written to
the stdin handler, they should be written through to the named pipe.