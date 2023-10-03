import queue
import threading

class QueueThread:
    def __init__(self):
        self.stdout = queue.Queue()
        self.stdin = queue.Queue()
        self.object = None

    def loop(self, my_queue):
        while True:
            try:
                if self.object != None:
                    item = self.stdout.get(timeout=1)
                    self.object.recieveData(item)
            except queue.Empty:
                pass 
        
    
    def start_thread(self):
        self.daemon_thread = threading.Thread(target=self.loop, args=(self.stdout,))
        self.daemon_thread.daemon = True 

        # Start the daemon thread
        self.daemon_thread.start()

    def addItem(self, item):
        #for the sake of testing, will send the command to the stdout queue
        self.stdout.put(item) 
    
    def loadObject(self, objectInstance):
        self.object = objectInstance
    
    def loadQueues(self, outputQueue, inputQueue):
        self.stdout = outputQueue
        self.stdin = inputQueue
