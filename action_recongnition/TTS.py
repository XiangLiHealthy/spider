import pyttsx3
from multiprocessing import Queue, Process
import time
import threading
from subprocess import call

class TTS :
    def __init__(self):
        #self.engine_ = pyttsx3.init()
        self.text_queue_ = Queue(50)
        #self.engine_.setProperty('voice', 'zh')
        #self.engine_.setProperty('rate', 200)
        return

    def say(self, text):
        #self.engine_.say(text)
        #call(["python3", "speak.py", text])
        #self.text_queue_.put(text)

        return

    def run(self):
        #self.engine_.runAndWait()
        return

def run(name, tts) :
    engine = pyttsx3.init()

    while True :
        text = tts.text_queue_.get()
        engine.say(text)
        engine.runAndWait()

    return

def runTTSProcess(tts) :
    #getter_process = Process(target=run, args=("Getter", tts))
    # putter_process = Process(target=putter, args=("Putter", queue))
    #getter_process.start()
    # putter_process.start()

    return

if __file__ == '__main__' :
    thread = threading()

