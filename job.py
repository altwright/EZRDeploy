import warnings
from pypsexec.client import Client
import threading

import time

from smbprotocol import Dialects
from smbprotocol._text import to_text

from smbprotocol.connection import (
    NtStatus,
    Connection,
    Request
)

from smbprotocol.exceptions import (
    SMBResponseException,
    SMBException,
    SMBUnsupportedFeature,
    SMB2SymbolicLinkErrorResponse
)

from smbprotocol.open import (
    CreateDisposition,
    CreateOptions,
    DirectoryAccessMask,
    FileAttributes,
    FileInformationClass,
    FilePipePrinterAccessMask,
    ImpersonationLevel,
    Open,
    ShareAccess,
    SMB2ReadRequest,
    ReadFlags,
    SMB2ReadResponse
)

from smbprotocol.tree import (
    TreeConnect,
)

from pypsexec.exceptions import (
    PypsexecException,
    PAExecException
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
    TheadCloseTimeoutWarning
)

from queue import Queue
import os.path
import smbclient.path

def _receive(connection: Connection, request, wait=True, timeout=None, resolve_symlinks=True):
    """
    Polls the message buffer of the TCP connection and waits until a valid
    message is received based on the message_id passed in.

    :param request: The Request object to wait get the response for
    :param wait: Wait for the final response in the case of a STATUS_PENDING response, the pending response is
        returned in the case of wait=False
    :param timeout: Set a timeout used while waiting for the final response from the server.
    :param resolve_symlinks: Set to automatically resolve symlinks in the path when opening a file or directory.
    :return: SMB2HeaderResponse of the received message
    """
    # Make sure the receiver is still active, if not this raises an exception.
    connection._check_worker_running()

    start_time = time.time()
    while True:
        iter_timeout = int(max(timeout - (time.time() - start_time), 1)) if timeout is not None else None
        if not request.response_event.wait(timeout=iter_timeout):
            raise SMBException(
                "Connection timeout of %d seconds exceeded while waiting for a message id %s "
                "response from the server" % (timeout, request.message["message_id"].get_value())
            )

        # Use a lock on the request so that in the case of a pending response we have exclusive lock on the event
        # flag and can clear it without the future pending response taking it over before we first clear the flag.
        with request.response_event_lock:
            connection._check_worker_running()  # The worker may have failed while waiting for the response, check again

            response = request.response
            status = response["status"].get_value()
            if status == NtStatus.STATUS_PENDING and wait:
                # Received a pending message, clear the response_event flag and wait again.
                request.response_event.clear()
                continue
            elif status == NtStatus.STATUS_STOPPED_ON_SYMLINK and resolve_symlinks:
                # Received when we do an Open on a path that contains a symlink. Need to capture all related
                # requests and resend the Open + others with the redirected path. First we need to resolve the
                # symlink path. This will fail if the symlink is pointing to a location that is not in the same
                # tree/share as the original request.

                # First wait for the other remaining requests to be processed. Their status will also fail and we
                # need to make sure we update the old request with the new one properly.
                related_requests = [connection.outstanding_requests[i] for i in request.related_ids]
                [r.response_event.wait() for r in related_requests]

                # Now create a new request with the new path the symlink points to.
                session = connection.session_table[request.session_id]
                tree = session.tree_connect_table[request.message["tree_id"].get_value()]

                old_create = request.get_message_data()
                tree_share_name = tree.share_name + "\\"
                original_path = tree_share_name + to_text(
                    old_create["buffer_path"].get_value(), encoding="utf-16-le"
                )

                exp = SMBResponseException(response)
                reparse_buffer = next(
                    (e for e in exp.error_details if isinstance(e, SMB2SymbolicLinkErrorResponse))
                )
                new_path = reparse_buffer.resolve_path(original_path)[len(tree_share_name) :]

                new_open = Open(tree, new_path)
                create_req = new_open.create(
                    old_create["impersonation_level"].get_value(),
                    old_create["desired_access"].get_value(),
                    old_create["file_attributes"].get_value(),
                    old_create["share_access"].get_value(),
                    old_create["create_disposition"].get_value(),
                    old_create["create_options"].get_value(),
                    create_contexts=old_create["buffer_contexts"].get_value(),
                    send=False,
                )[0]

                # Now add all the related requests (if any) to send as a compound request.
                new_msgs = [create_req] + [r.get_message_data() for r in related_requests]
                new_requests = connection.send_compound(new_msgs, session.session_id, tree.tree_connect_id, related=True)

                # Verify that the first request was successful before updating the related requests with the new
                # info.
                error = None
                try:
                    new_response = _receive(connection, new_requests[0], wait=wait, timeout=timeout, resolve_symlinks=True)
                except SMBResponseException as exc:
                    # We need to make sure we fix up the remaining responses before throwing this.
                    error = exc
                [r.response_event.wait() for r in new_requests]

                # Update the old requests with the new response information
                for i, old_request in enumerate([request] + related_requests):
                    del connection.outstanding_requests[old_request.message["message_id"].get_value()]
                    old_request.update_request(new_requests[i])

                if error:
                    raise error

                return new_response
            else:
                # now we have a retrieval request for the response, we can delete
                # the request from the outstanding requests
                message_id = request.message["message_id"].get_value()
                connection.outstanding_requests.pop(message_id, None)

                if status == NtStatus.STATUS_CANCELLED:
                    return None

                if status not in [NtStatus.STATUS_SUCCESS, NtStatus.STATUS_PENDING, NtStatus.STATUS_CANCELLED]:
                    raise SMBResponseException(response)
                
                break

    return response

def _get_main_pipe_request(main_pipe: Open, offset, length, min_length=0, unbuffered=False, send=True) -> Request:
    # Start of Open.read()
    if length > main_pipe.connection.max_read_size:
        raise SMBException(
            "The requested read length %d is greater than "
            "the maximum negotiated read size %d" % (length, main_pipe.connection.max_read_size)
        )

    read = SMB2ReadRequest()
    read["length"] = length
    read["offset"] = offset
    read["minimum_count"] = min_length
    read["file_id"] = main_pipe.file_id
    read["padding"] = b"\x50"

    if unbuffered:
        if main_pipe.connection.dialect < Dialects.SMB_3_0_2:
            raise SMBUnsupportedFeature(
                main_pipe.connection.dialect, Dialects.SMB_3_0_2, "SMB2_READFLAG_READ_UNBUFFERED", True
            )
        read["flags"].set_flag(ReadFlags.SMB2_READFLAG_READ_UNBUFFERED)

    if not send:
        return read, main_pipe._read_response

    return main_pipe.connection.send(read, main_pipe.tree_connect.session.session_id, main_pipe.tree_connect.tree_connect_id)
    # End of Open.read()

def _get_main_pipe_response(request: Request, main_pipe: Open, wait = True):
    # Start of Open._read_response()
    response = _receive(main_pipe.connection, request, wait=wait)
    if response is None:
        return None
    else:
        read_response = SMB2ReadResponse()
        read_response.unpack(response["data"].get_value())

        return read_response["buffer"].get_value()

def file_out_stream(filepath: str, buffer_size: int = 4096):
    f = open(filepath, "rb")
    byte_count = os.path.getsize(f.fileno())
    for i in range(0, byte_count, buffer_size):
        yield f.read(buffer_size), i
    f.close()

class Job(threading.Thread):

    def __init__(
            self,
            client: Client, 
            executable: str, 
            arguments: str, 
            stdoutQ: Queue, 
            stderrQ: Queue,
            stdinQ: Queue,
            copy_local_exe: bool = False,
            local_exe_src_dir: str = "",
            clean_copied_exe_after: bool = False,
            overwrite_remote_exe: bool = False,
            copy_local_files: bool = False,
            src_files_list: list[str] = None,
            overwrite_remote_files: bool = False,
            clean_copied_files_after: bool = False,
            processors=None,
            use_system_account=False,
            working_dir: str = None,
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
        self.copy_local_exe = copy_local_exe
        self.local_exe_src_dir = local_exe_src_dir
        self.clean_copied_exe_after = clean_copied_exe_after
        self.copy_local_files = copy_local_files
        self.src_files_list = src_files_list
        self.clean_copied_files_after = clean_copied_files_after
        self.overwrite_remote_exe = overwrite_remote_exe
        self.overwrite_remote_files = overwrite_remote_files

        self.ADMIN_SHARE = r"\\%s\ADMIN$" % self.client.connection.server_name
        self.C_SHARE = r"\\%s\C$" % self.client.connection.server_name

        if self.working_dir:
            working_dir_tail = os.path.splitdrive(self.working_dir)[1]
            self.remote_file_dst_dir = os.path.join(self.C_SHARE, working_dir_tail)
        else:
            self.remote_file_dst_dir = self.C_SHARE

        self.remote_exe_path = os.path.join(self.ADMIN_SHARE, self.executable)
        self.rc = None
        self.stdoutBuffer: bytes = b""

        self.main_pipe_request: Request = None
    
    def _copy_local_files(self):
        if self.copy_local_exe:
            remote_exe_exists = smbclient.path.exists(self.remote_exe_path)
            if not remote_exe_exists or self.overwrite_remote_exe:
                local_exe_path = os.path.join(self.local_exe_src_dir, self.executable)
                with smbclient.open_file(self.remote_exe_path, "wb") as remote_fd:
                    for (data, offset) in file_out_stream(local_exe_path, self.client.connection.max_write_size):
                        remote_fd.write(data)
        
        if self.copy_local_files and (self.src_files_list is not None):
            if not smbclient.path.exists(self.remote_file_dst_dir):
                smbclient.mkdir(self.remote_file_dst_dir)
            for src_file in self.src_files_list:
                remote_file_path = os.path.join(self.remote_file_dst_dir, os.path.basename(src_file))
                if self.overwrite_remote_files or not smbclient.path.exists(remote_file_path):
                    with smbclient.open_file(remote_file_path, "wb") as remote_fd:
                        for (data, offset) in file_out_stream(src_file, self.client.connection.max_write_size):
                            remote_fd.write(data)

    def _clean_remote_files(self):
        if self.copy_local_exe and self.clean_copied_exe_after:
            smbclient.remove(self.remote_exe_path)

        if self.copy_local_files and self.clean_copied_files_after:
            for src_file in self.src_files_list:
                smbclient.remove(os.path.join(self.remote_file_dst_dir, os.path.basename(src_file)))

    def run(self):
        self._copy_local_files()

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
        stdout_pipe = StdoutPipe(smb_tree, self.client._stdout_pipe_name, self.stdoutQ, self.stdoutBuffer)
        stdout_pipe.start()
        stderr_pipe = StdoutPipe(smb_tree, self.client._stderr_pipe_name, self.stderrQ, self.stdoutBuffer)
        stderr_pipe.start()
        
        input_finished_event = threading.Event()
        stdin_pipe = StdinPipe(smb_tree, self.client._stdin_pipe_name, self.stdinQ, input_finished_event)
        stdin_pipe.start()

        # wait until the stdout and stderr pipes have sent their first
        # response
        while not stdout_pipe.sent_first:
            pass
        while not stderr_pipe.sent_first:
            pass

        # Block until final exit response from the process is read
        self.main_pipe_request = _get_main_pipe_request(main_pipe, 0, 1024)
        exe_result_raw = _get_main_pipe_response(self.main_pipe_request, main_pipe)

        input_finished_event.set()

        stdout_pipe.close()
        stderr_pipe.close()
        stdin_pipe.close()

        main_pipe.close()
        smb_tree.disconnect()

        if exe_result_raw is not None:
            exe_result = PAExecMsg()
            exe_result.unpack(exe_result_raw)
            try:
                exe_result.check_resp()
            except PAExecException as exc:
                self.stderrQ.put(exc.message)
            rc = PAExecReturnBuffer()
            rc.unpack(exe_result['buffer'].get_value())

            self.rc = rc['return_code'].get_value()

        self._clean_remote_files()
        self.main_pipe_request = None
    
    def cancel(self):
        if self.main_pipe_request is not None:
            self.main_pipe_request.cancel()

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
            try:
                self.pipe.close(get_attributes=False)
            except KeyError as exc:#I don't know why it happens sometimes
                pass

    def write(self, data):
        self.pipe.write(data, 0)

    def close(self):
        self.pipe.close(get_attributes=False)
        self.join(timeout=5)
        if self.is_alive():
            warnings.warn("Timeout while waiting for pipe thread to close: %s"
                          % self.name, TheadCloseTimeoutWarning)

class StdoutPipe(OutputPipe):

    def __init__(self, tree, name, stdoutQ: Queue, stdoutBuffer: bytes):
        super(StdoutPipe, self).__init__(tree, name)
        self.pipe_buffer = stdoutBuffer
        self.stdoutQ = stdoutQ

    def handle_output(self, output: bytes):
        self.pipe_buffer += output
        self.stdoutQ.put(output.decode())

    def get_output(self):
        return self.pipe_buffer