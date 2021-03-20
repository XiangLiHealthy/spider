from action_recongnition import ActionRecongnition
from multiprocessing import Queue, Process
#from Queue import Empty as QueueEmpty
import random
import time

queue = Queue(30)
action_recong_engine = ActionRecongnition(queue)

def getter(name, queue):
  action_recong_engine.fetchFrameThread()
  print('get process exit')

  # block为True,就是如果队列中无数据了。
  #   |—————— 若timeout默认是None，那么会一直等待下去。
  #   |—————— 若timeout设置了时间，那么会等待timeout秒后才会抛出Queue.Empty异常
  # block 为False，如果队列中无数据，就抛出Queue.Empty异常

if __name__ == "__main__":
  print('------start------')

  try:
    getter_process = Process(target=getter, args=("Getter", queue))
    getter_process.start()

    action_recong_engine.recongActionThread()
  except Exception as e:
    print (e)

  print ('-------end----')
