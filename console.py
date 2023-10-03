from queue import Queue
import threading
import time

class ConsoleThread:
    def __init__(self):
        self.stdoutQ: Queue = None
        self.stdinQ: Queue = None
        self.object = None
        self._pause_event = threading.Event()

    def loop(self, my_queue):
        while not self._stop_event.is_set():
            item = self.stdoutQ.get(timeout=1)
            self.callBack(item)
        
    def start_thread(self):
        self.daemon_thread = threading.Thread(target=self.loop, args=(self.stdout,))
        self.daemon_thread.daemon = True 

        self.daemon_thread.start()

    def addItem(self, item):
        #for the sake of testing, will send the command to the stdout queue
        self.stdoutQ.put(item) 
    
    def loadObject(self, objectInstance):
        self.object = objectInstance
    
    def loadQueues(self, stdoutQ: Queue, stdinQ: Queue):
        self.stdoutQ= stdoutQ
        self.stdinQ = stdinQ

    def pause_thread(self):
        self._pause_event.set()

    def resume_thread(self):
        self._pause_event.clear() 