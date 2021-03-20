from action_recongnition import ActionRecongnition
from multiprocessing import Queue, Process
#from Queue import Empty as QueueEmpty
import random
import time

image_queue = Queue(50)
recong_queue = Queue(150)

action_recong_engine = ActionRecongnition(image_queue, recong_queue)


def getter(name, queue):
  action_recong_engine.fetchFrameThread()
  print('get process exit')


def putter(name, queue):
  action_recong_engine.recongActionThread()


if __name__ == '__main__':
  queue = Queue()
  getter_process = Process(target=getter, args=("Getter", queue))
  putter_process = Process(target=putter, args=("Putter", queue))
  getter_process.start()
  putter_process.start()


  print('------start------')

  try:
    action_recong_engine.drawVideoThread()
  except Exception as e:
    print (e)

  print ('-------end----')
