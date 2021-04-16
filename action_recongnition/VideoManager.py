import cv2

class VideoManager :
    def __init__(self):
        self.file_name_ = ''
        self.cap_ = None
        self.cache_ = []

        return

    def setVideo(self, file_name):
        if file_name == self.file_name_ :
            return

        # laoding video
        self.cap_ = cv2.VideoCapture(file_name)

        return

    def get_frame_cache(self, idx):
        for item in self.cache_ :
            if item['idx'] == idx :
                return item['image']

        return None

    def getFrameByIdx(self, idx):
        # frame = self.get_frame_cache(idx)
        # if None == frame :
        #     self.cap_.set(cv2.CAP_PROP_POS_FRAMES, idx)
        #     success, frame = self.cap_.read()
        #     item = {}
        #     item['idx'] = idx
        #     item['image'] = frame
        #     self.cache_.append(item)
        self.cap_.set(cv2.CAP_PROP_POS_FRAMES, idx)
        success, frame = self.cap_.read()
        return frame

    def getFrameCount(self):

        return self.cap_.get(7)

    def release(self):
        self.cap_.release()
        self.cache_.clear()