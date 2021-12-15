from queue import Queue

class SearchableQueue(Queue):
  def __init__(self, maxsize: int = 10) -> None:
      super().__init__(maxsize=maxsize)

  ''' This is a simple method to check if an item is on the queue by checking one obj key.
  If no key is provided, it means the queue has primitives values.
  '''
  def lookup(self, value, key = None):
    if self.qsize() == 0:
      return False

    isOnQueue = False
    if key is not None:
      for obj in self.queue:
        if hasattr(obj, key):
          if getattr(obj, key) == value:
            isOnQueue = True
    else:
      for item in self.queue:
        if item == value:
          isOnQueue = True

    return isOnQueue