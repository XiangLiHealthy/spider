import pyttsx3

class TTS :
    def __init__(self):
        self.engine_ = pyttsx3.init()

        self.engine_.setProperty('voice', 'zh')
        self.engine_.setProperty('rate', 200)

    def say(self, text):
        self.engine_.say(text)

        return

    def run(self):
        self.engine_.runAndWait()

        return

