import time
from SearchableQueue import SearchableQueue

class TitleQueueHandler:
  def __init__(self, titleType, rokBotQueue):
    self.queue = SearchableQueue()
    self.rokBotQueue = rokBotQueue
    self.type = titleType
    self.currentUser = None
    self.currentOrder = None
    self.isDone = False

  def start(self):
    while True:
      self.currentOrder = self.queue.get()
      print(f'Queue {self.type} received a request.')
      
      # Saves the user that has originated the request
      self.currentUser = self.currentOrder.orderer

      self.rokBotQueue.put(self.currentOrder)

      # TODO Set how much time an user can stay with the title.
      self.timer(12000)

      self.currentUser = None

      print(f'Queue {self.type} task finished.')

      self.currentOrder = None
      self.queue.task_done()

  def put(self, order):
    try:
      self.queue.put(order)
      return True
    except Exception as exception:
      print(exception)
      print(f'Failed to add request {order} to queue {self.type}')
      return False
  
  def done(self, userName):
    # Finalize the request only if the user owns the reservation
    if (self.currentUser == userName):
      self.isDone = True
      return True

  def isUserOnQueue(self, order):
    if self.currentOrder is not None and self.currentOrder.orderer == order.orderer:
      return True

    return self.queue.lookup(order.orderer, 'orderer')
  
  def timer(self, timeout):
    self.isDone = False
    startTime = time.perf_counter()
    while time.perf_counter() - startTime < timeout and not self.isDone:
      time.sleep(1)

