from queue import Queue
import threading
import time
import queue

class ConsoleThread:
    def __init__(self):
        self.stdoutQ: Queue = None
        self.stdinQ: Queue = None
        self.currentRunningTaskTab = None
        self._pause_event = threading.Event()

    def loop(self):
        while True:
            if self.currentRunningTaskTab:
                if self.stdoutQ is not None and not self.stdoutQ.empty():
                    stdoutStr = self.stdoutQ.get()
                    print("string is:" + stdoutStr + "|")
                    self.currentRunningTaskTab.print_new_stdout_to_console(stdoutStr)
            if self._pause_event.is_set():
                # The thread is paused, so it waits until resumed
                self._pause_event.wait()
        
    def start_thread(self):
        self.daemon_thread = threading.Thread(target=self.loop)
        self.daemon_thread.daemon = True 

        self.daemon_thread.start()
    
    def loadRunningTaskTab(self, runningTaskTab):
        self.currentRunningTaskTab = runningTaskTab
    
    def loadQueues(self, stdoutQ: Queue, stdinQ: Queue):
        self.stdoutQ= stdoutQ
        self.stdinQ = stdinQ

    def pause_thread(self):
        self._pause_event.set()

    def resume_thread(self):
        self._pause_event.clear() 