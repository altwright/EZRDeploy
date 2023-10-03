import queue
import threading

class QueueThread:
    def __init__(self, callBack):
        self.stdout = queue.Queue()
        self.stdin = queue.Queue()
        self.callBack = callBack
        self._stop_event = threading.Event()

    def loop(self, my_queue):
        while not self._stop_event.is_set():
            try:
                item = self.stdout.get(timeout=1)
                self.callBack(item)
            except queue.Empty:
                pass 
        
    
    def start_thread(self):
        self.daemon_thread = threading.Thread(target=self.loop, args=(self.stdout,))
        self.daemon_thread.daemon = True  # Mark the thread as a daemon thread

        # Start the daemon thread
        self.daemon_thread.start()

    def addItem(self, item):
        #for the sake of testing, will send the command to the stdout queue
        self.stdout.put(item) 
    
    def loadQueues(self, outputQueue, inputQueue):
        self.stdout = outputQueue
        self.stdin = inputQueue
    
    def stop_thread(self):
        self._stop_event.set()