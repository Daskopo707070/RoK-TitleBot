import queue
import time

class RokBot:
  def __init__(self):
    self.queue = queue.Queue()

  def start(self):
    while True:
      order = self.queue.get()
      self.log('Task received.')
      self.processRequest(order)
      self.queue.task_done()

  def processRequest(self, order):
    self.log(f'Giving title {order.title} to user {order.orderer}')
    # TODO: Somehow execute the intended action in RoK
    time.sleep(1)
    self.log('Request finished')

  def log(self, message):
    prefix = 'RoK Bot: '
    print(prefix + message)