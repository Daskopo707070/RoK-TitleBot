import queue
import time
import threading

class RokBot:
  def __init__(self):
    self.queue = queue.Queue()
    threading.Thread(target=self.captchaSolver, daemon=True).start()

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
  
  # This function is supose to run in another thread. It is a infine loop 
  # with 7.5min (450 seconds) interval (configurable).
  def captchaSolver(self, interval=450):
    while True:
      # TODO: Run a function to resolve captcha.
      time.sleep(interval)