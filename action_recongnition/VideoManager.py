import cv2

class VideoManager :
    def __init__(self):
        self.file_name_ = ''
        self.cap_ = None
        self.cache_ = []
        self.last_idx = -1
        self.image_ = None

        return

    def setVideo(self, file_name):
        if file_name == self.file_name_ :
            return

        # laoding video
        self.cap_ = cv2.VideoCapture(file_name)
        self.last_idx = -1
        self.image_ = None

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
        if idx == self.last_idx :
            return self.image_

        self.cap_.set(cv2.CAP_PROP_POS_FRAMES, idx)
        success, frame = self.cap_.read()
        frame = cv2.flip(frame, 1)

        self.last_idx = idx
        self.image_ = frame

        return frame

    def getFrameCount(self):

        return self.cap_.get(7)

    def release(self):
        self.cap_.release()
        self.cache_.clear()