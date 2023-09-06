import warnings
from pypsexec.client import Client
from pypsexec.pipe import TheadCloseTimeoutWarning
import threading
import sys

import time

from smbprotocol.connection import (
    NtStatus,
)

from smbprotocol.exceptions import (
    SMBResponseException,
)

from smbprotocol.open import (
    FilePipePrinterAccessMask,
    Open
)

from smbprotocol.tree import (
    TreeConnect,
)

from pypsexec.exceptions import (
    PypsexecException,
)

from pypsexec.paexec import (
    PAExecMsg,
    PAExecMsgId,
    PAExecReturnBuffer,
    PAExecSettingsBuffer,
    PAExecSettingsMsg,
    PAExecStartBuffer,
    ProcessPriority,
)

from pypsexec.pipe import (
    OutputPipe,
    open_pipe,
)

from queue import Queue

class JobThread(threading.Thread):

    def __init__(
            self,
            client: Client, 
            executable: str, 
            arguments: str, 
            stdoutQ: Queue, 
            stderrQ: Queue,
            stdinQ: Queue,
            input_finished_event: threading.Event = threading.Event(),
            processors=None,
            use_system_account=False,
            working_dir=None,
            priority=ProcessPriority.NORMAL_PRIORITY_CLASS,
            remote_log_path=None, 
            timeout_seconds=0,
            wow64=False):

        threading.Thread.__init__(self)
        self.client = client
        self.executable = executable
        self.stdoutQ = stdoutQ
        self.stderrQ = stderrQ
        self.stdinQ = stdinQ
        self.arguments = arguments
        self.processors = processors
        self.use_system_account = use_system_account
        self.working_dir = working_dir
        self.priority = priority
        self.remote_log_path = remote_log_path
        self.timeout_seconds = timeout_seconds
        self.wow64 = wow64
        self.input_finished_event = input_finished_event

        self.rc = None
    
    def run(self):
        self.client._service.start()

        smb_tree = TreeConnect(self.client.session,
                               r"\\%s\IPC$" % self.client.connection.server_name)
        smb_tree.connect()

        settings = PAExecSettingsBuffer()
        settings['processors'] = self.processors if self.processors else []
        settings['asynchronous'] = False
        settings['dont_load_profile'] = False
        settings['interactive_session'] = 0
        settings['interactive'] = False
        settings['run_elevated'] = False
        settings['run_limited'] = False
        settings['username'] = self.client._encode_string(None)
        settings['password'] = self.client._encode_string(None)
        settings['use_system_account'] = self.use_system_account
        settings['working_dir'] = self.client._encode_string(self.working_dir)
        settings['show_ui_on_win_logon'] = False
        settings['priority'] = self.priority
        settings['executable'] = self.client._encode_string(self.executable)
        settings['arguments'] = self.client._encode_string(self.arguments)
        settings['remote_log_path'] = self.client._encode_string(self.remote_log_path)
        settings['timeout_seconds'] = self.timeout_seconds
        settings['disable_file_redirection'] = not self.wow64

        input_data = PAExecSettingsMsg()
        input_data['unique_id'] = self.client._unique_id
        input_data['buffer'] = settings

        # write the settings to the main PAExec pipe
        pipe_access_mask = FilePipePrinterAccessMask.GENERIC_READ | \
            FilePipePrinterAccessMask.GENERIC_WRITE | \
            FilePipePrinterAccessMask.FILE_APPEND_DATA | \
            FilePipePrinterAccessMask.READ_CONTROL | \
            FilePipePrinterAccessMask.SYNCHRONIZE
        for i in range(0, 3):
            try:
                main_pipe = open_pipe(smb_tree, self.client._exe_file,
                                      pipe_access_mask)
            except SMBResponseException as exc:
                if exc.status != NtStatus.STATUS_OBJECT_NAME_NOT_FOUND:
                    raise exc
                elif i == 2:
                    raise PypsexecException("Failed to open main PAExec pipe "
                                            "%s, no more attempts remaining"
                                            % self.client._exe_file)
                time.sleep(5)
            else:
                break

        main_pipe.write(input_data.pack(), 0)

        settings_resp_raw = main_pipe.read(0, 1024)
        settings_resp = PAExecMsg()
        settings_resp.unpack(settings_resp_raw)
        settings_resp.check_resp()

        # start the process now
        start_msg = PAExecMsg()
        start_msg['msg_id'] = PAExecMsgId.MSGID_START_APP
        start_msg['unique_id'] = self.client._unique_id
        start_msg['buffer'] = PAExecStartBuffer()
        start_buffer = PAExecStartBuffer()
        start_buffer['process_id'] = self.client.pid
        start_buffer['comp_name'] = self.client.current_host.encode('utf-16-le')
        start_msg['buffer'] = start_buffer

        main_pipe.write(start_msg.pack(), 0)

        # create a pipe for stdout, stderr, and stdin and run in a separate
        # thread
        stdout_pipe = StdoutPipe(smb_tree, self.client._stdout_pipe_name, self.stdoutQ)
        stdout_pipe.start()
        stderr_pipe = StdoutPipe(smb_tree, self.client._stderr_pipe_name, self.stderrQ)
        stderr_pipe.start()
        
        stdin_pipe = StdinPipe(smb_tree, self.client._stdin_pipe_name, self.stdinQ, self.input_finished_event)
        stdin_pipe.start()

        # wait until the stdout and stderr pipes have sent their first
        # response
        while not stdout_pipe.sent_first:
            pass
        while not stderr_pipe.sent_first:
            pass

        # Block until final exit response from the process is read
        exe_result_raw = main_pipe.read(0, 1024)
        self.input_finished_event.set()

        stdout_pipe.close()
        stderr_pipe.close()
        stdin_pipe.close()

        main_pipe.close()
        smb_tree.disconnect()

        exe_result = PAExecMsg()
        exe_result.unpack(exe_result_raw)
        exe_result.check_resp()
        rc = PAExecReturnBuffer()
        rc.unpack(exe_result['buffer'].get_value())

        self.rc = rc['return_code'].get_value()

class StdinPipe(threading.Thread):

    def __init__(self, tree, name, inputQueue: Queue, finished: threading.Event):
        """
        Any data sent to write is written to the Named Pipe.

        :param tree: The SMB tree connected to IPC$
        :param name: The name of the input Named Pipe
        """
        threading.Thread.__init__(self)

        self.name = name
        self.connection = tree.session.connection
        self.sid = tree.session.session_id
        self.tid = tree.tree_connect_id
        self.pipe = open_pipe(tree, name,
                              FilePipePrinterAccessMask.FILE_WRITE_DATA |
                              FilePipePrinterAccessMask.FILE_APPEND_DATA |
                              FilePipePrinterAccessMask.FILE_WRITE_EA |
                              FilePipePrinterAccessMask.FILE_WRITE_ATTRIBUTES |
                              FilePipePrinterAccessMask.FILE_READ_ATTRIBUTES |
                              FilePipePrinterAccessMask.READ_CONTROL |
                              FilePipePrinterAccessMask.SYNCHRONIZE,
                              fsctl_wait=True)
        self.inpQueue = inputQueue
        self.finished = finished

    def run(self):
        try:
            while not self.finished.is_set():
                if not self.inpQueue.empty():
                    self.write(bytes(self.inpQueue.get(), 'utf-8'))
        except SMBResponseException as exc:
            # if the error was the pipe was broken exit the loop
            # otherwise the error is serious so throw it
            close_errors = [
                NtStatus.STATUS_PIPE_BROKEN,
                NtStatus.STATUS_PIPE_CLOSING,
                NtStatus.STATUS_PIPE_EMPTY,
                NtStatus.STATUS_PIPE_DISCONNECTED,
                NtStatus.STATUS_FILE_CLOSED
            ]
            if exc.status not in close_errors:
                raise exc
        finally:
            self.pipe.close(get_attributes=False)

    def write(self, data):
        self.pipe.write(data, 0)

    def close(self):
        self.pipe.close(get_attributes=False)
        self.join(timeout=5)
        if self.is_alive():
            warnings.warn("Timeout while waiting for pipe thread to close: %s"
                          % self.name, TheadCloseTimeoutWarning)

class StdoutPipe(OutputPipe):

    def __init__(self, tree, name, stdoutQ: Queue):
        super(StdoutPipe, self).__init__(tree, name)
        self.pipe_buffer = b""
        self.stdoutQ = stdoutQ

    def handle_output(self, output: bytes):
        self.pipe_buffer += output
        self.stdoutQ.put(output.decode())

    def get_output(self):
        return self.pipe_buffer

def execute_job(client: Client, executable: str, arguments: str = None, 
                    processors=None,
                    use_system_account=False,
                    working_dir=None,
                    priority=ProcessPriority.NORMAL_PRIORITY_CLASS,
                    remote_log_path=None, timeout_seconds=0,
                    wow64=False, 
                    stdoutQ: Queue = Queue(), stderrQ: Queue = Queue(), stdinQ: Queue = Queue()):

        client._service.start()

        smb_tree = TreeConnect(client.session,
                               r"\\%s\IPC$" % client.connection.server_name)
        smb_tree.connect()

        settings = PAExecSettingsBuffer()
        settings['processors'] = processors if processors else []
        settings['asynchronous'] = False
        settings['dont_load_profile'] = False
        settings['interactive_session'] = 0
        settings['interactive'] = False
        settings['run_elevated'] = False
        settings['run_limited'] = False
        settings['username'] = client._encode_string(None)
        settings['password'] = client._encode_string(None)
        settings['use_system_account'] = use_system_account
        settings['working_dir'] = client._encode_string(working_dir)
        settings['show_ui_on_win_logon'] = False
        settings['priority'] = priority
        settings['executable'] = client._encode_string(executable)
        settings['arguments'] = client._encode_string(arguments)
        settings['remote_log_path'] = client._encode_string(remote_log_path)
        settings['timeout_seconds'] = timeout_seconds
        settings['disable_file_redirection'] = not wow64

        input_data = PAExecSettingsMsg()
        input_data['unique_id'] = client._unique_id
        input_data['buffer'] = settings

        # write the settings to the main PAExec pipe
        pipe_access_mask = FilePipePrinterAccessMask.GENERIC_READ | \
            FilePipePrinterAccessMask.GENERIC_WRITE | \
            FilePipePrinterAccessMask.FILE_APPEND_DATA | \
            FilePipePrinterAccessMask.READ_CONTROL | \
            FilePipePrinterAccessMask.SYNCHRONIZE
        for i in range(0, 3):
            try:
                main_pipe = open_pipe(smb_tree, client._exe_file,
                                      pipe_access_mask)
            except SMBResponseException as exc:
                if exc.status != NtStatus.STATUS_OBJECT_NAME_NOT_FOUND:
                    raise exc
                elif i == 2:
                    raise PypsexecException("Failed to open main PAExec pipe "
                                            "%s, no more attempts remaining"
                                            % client._exe_file)
                time.sleep(5)
            else:
                break

        main_pipe.write(input_data.pack(), 0)

        settings_resp_raw = main_pipe.read(0, 1024)
        settings_resp = PAExecMsg()
        settings_resp.unpack(settings_resp_raw)
        settings_resp.check_resp()

        # start the process now
        start_msg = PAExecMsg()
        start_msg['msg_id'] = PAExecMsgId.MSGID_START_APP
        start_msg['unique_id'] = client._unique_id
        start_msg['buffer'] = PAExecStartBuffer()
        start_buffer = PAExecStartBuffer()
        start_buffer['process_id'] = client.pid
        start_buffer['comp_name'] = client.current_host.encode('utf-16-le')
        start_msg['buffer'] = start_buffer

        main_pipe.write(start_msg.pack(), 0)

        # create a pipe for stdout, stderr, and stdin and run in a separate
        # thread
        stdout_pipe = StdoutPipe(smb_tree, client._stdout_pipe_name, stdoutQ)
        stdout_pipe.start()
        stderr_pipe = StdoutPipe(smb_tree, client._stderr_pipe_name, stderrQ)
        stderr_pipe.start()
        input_finished = threading.Event()
        stdin_pipe = StdinPipe(smb_tree, client._stdin_pipe_name, stdinQ, input_finished)
        stdin_pipe.start()

        # wait until the stdout and stderr pipes have sent their first
        # response
        while not stdout_pipe.sent_first:
            pass
        while not stderr_pipe.sent_first:
            pass

        # read the final response from the process
        exe_result_raw = main_pipe.read(0, 1024)
        input_finished.set()

        stdout_pipe.close()
        stderr_pipe.close()
        stdin_pipe.close()
        stdout_out = stdout_pipe.get_output()
        stderr_bytes = stderr_pipe.get_output()

        main_pipe.close()
        smb_tree.disconnect()

        exe_result = PAExecMsg()
        exe_result.unpack(exe_result_raw)
        exe_result.check_resp()
        rc = PAExecReturnBuffer()
        rc.unpack(exe_result['buffer'].get_value())

        return_code = rc['return_code'].get_value()
        return stdout_out, stderr_bytes, return_code
