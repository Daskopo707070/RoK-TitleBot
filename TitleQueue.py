import queue
import time

class TitleQueue:
  def __init__(self, titleType, rokBotQueue):
    self.queue = queue.Queue()
    self.rokBotQueue = rokBotQueue
    self.type = titleType
    self.currentUser = None
    self.isDone = False

  def start(self):
    while True:
      order = self.queue.get()
      print(f'Queue {self.type} received a request.')
      
      # Saves the user that has originated the request
      self.currentUser = order.orderer

      self.rokBotQueue.put(order)

      # TODO Set how much time an user can stay with the title.
      self.timer(12000)

      self.currentUser = None

      print(f'Queue {self.type} task finished.')
      self.queue.task_done()

  def put(self, order):
    self.queue.put(order)
  
  def done(self, userName):
    # Finalize the request only if the user owns the reservation
    if (self.currentUser == userName):
      print(f'User {userName} done with {self.type}.')
      self.isDone = True
  
  def timer(self, timeout):
    self.isDone = False
    startTime = time.perf_counter()
    while time.perf_counter() - startTime < timeout and not self.isDone:
      time.sleep(1)

