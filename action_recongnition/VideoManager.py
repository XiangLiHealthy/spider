import cv2

class VideoManager :
    def __init__(self):
        self.file_name_ = ''
        self.cap_ = None

        return

    def setVideo(self, file_name):
        if file_name == self.file_name_ :
            return

        # laoding video
        self.cap_ = cv2.VideoCapture(file_name)

        return

    def getFrameByIdx(self, idx):
        self.cap_.set(cv2.CAP_PROP_POS_FRAMES, idx)

        success, frame = self.cap_.read()

        return frame

    def getFrameCount(self):

        return

    def release(self):
        self.cap_.release()
