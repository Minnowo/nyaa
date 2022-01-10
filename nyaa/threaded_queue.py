

import threading 

active_threads = {
    
}

class WorkerQueue():

    def __init__(self, function) -> None:
        
        self.alive = True 
        self.items = []

        self.callback = function

        self.signal = threading.Event()
        self.thread = threading.Thread(target=self.__worker_thread)
        self.thread.start()

    def enqueue(self, item):
        # enqueue the item and set the flag -> True 
        self.items.append(item)
        self.signal.set()

    def __worker_thread(self):
        
        # keep thread waiting
        while True:
            
            # if there are items in the queue
            # process until the queue is empty 
            if self.items:
                # invoke the callback given by the user and return their item 
                # print("processing items")
                self.callback(self.items.pop(0))

            else:
                # only kill thread after all items have been processed with
                if not self.alive:
                    break

                # reset the flag and pause the thread
                self.signal.clear()
                self.signal.wait()


    def cleanup(self):
        
        # allow while loop to end
        self.alive = False

        # trigger signal to end while loop
        self.signal.set()

        # cleanup our thread 
        self.thread.join()
