from action_recongnition import ActionRecongnition

if __name__ == "__main__":
  print('------start------')

  try:
    action_recong_engine = ActionRecongnition()
    action_recong_engine.startup()

  except Exception as e:
    print (e)

  print ('-------end----')

