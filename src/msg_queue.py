import Queue

class MessageQueue:

    def __init__(self):
        self.queue = Queue.Queue()

    # Get the latest unprocessed msg
    def get(self):
        print "Hello get"
        if not self.queue.empty():
            item = self.queue.get_nowait()
            return item.msg

    # Put the received msg into the list
    def put(self, msg):
        self.queue.put( msg )

    # Get all items
    def get_all(self):
        items = []
        while 1:
            try:
                items.append(self.queue.get_nowait())
            except Queue.Empty:
                print "Exception"
                break
        print items
        return items