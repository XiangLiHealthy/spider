import cv2

from EvaluationModel import EvaluationModel
from enum import Enum
from ConfigManager import g_config

class EvaluationState(Enum) :

    INIT = 0
    TEACHING = -1
    PREPARE = 1
    EVALUATING = 2
    KEEP_POSE = 3
    COMPLETE = 4

class Prepare :
    def __init__(self, context):
        self.teacher_landmarks_ = {}
        self.teacher_image_ = None
        self.context_ = EvaluationModel() #context
        self.pose_idx_ = 0

        return

    def setTeacherPose(self):
        # 1. get first pose landmarks and image
        pose = self.context_.teacher_action_.m_teacher_pose[self.pose_idx_]
        self.teacher_landmarks_ = pose['landmarks']

        # 2.
        idx = pose['frame_num']
        self.teacher_image_ = self.context_.video_manager_.getFrameByIdx(idx)

        return

    def drawTeacherTips(self):
        tips = self.context_.teacher_action_.m_teacher_pose[self.pose_idx_]['tips']

        point = (40, 40)
        cv2.putText(self.context_.evaluation_image_, tips, point, cv2.FONT_HERSHEY_PLAIN, 2.0,
                    (0, 0, 255), 2)

        return

    def perform(self, user_landmarks, user_image):
        # 1.set teacher pose
        self.setTeacherPose()

        # 2. show teacher tips
        self.drawTeacherTips()

        # 3. recong user pose
        
        # 4. error tips

        return

class Teaching :
    def __init__(self, context):
        self.context_ = EvaluationModel() #context
        self.video_idx_ = 0
        self.play_times_ = 0
        self.video_path_ = ''

        return

    def setImage(self):
        if self.video_path_ != self.context_.current_task_.j_config_['video_path']:
            self.video_path_ = self.context_.current_task_.j_config_['video_path']
            self.video_idx_ = 0
            self.play_times_ = 0
            self.context_.video_manager_.setVideo(self.video_path_)

        self.context_.evaluation_image_ = self.context_.video_manager_.getFrameByIdx(self.video_idx_)
        self.video_idx_idx_ += 1

        return

    def showTips(self, user_imnage):
        # where can L get tips content
        tips = ''

        point = (40, 40)
        cv2.putText(self.context_.evaluation_image_, tips, point, cv2.FONT_HERSHEY_PLAIN, 2.0,
                    (0, 0, 255), 2)

        return

    def perform(self, user_landmarks, user_image):
        # 1.play video
        self.setImage()

        # 2.tips text
        self.showTips(user_image)

        # increament times if play ok
        if self.context_.video_manager_.getFrameCount() == self.video_idx_ :
            self.play_times_ += 1
            self.video_idx_ = 0

        # return next state if times ok
        state = EvaluationState.TEACHING
        if self.context_.current_task_.j_config_['play_times'] <= self.play_times_ :
            state = EvaluationState.PREPARE

        return state

class Evaluating :
    def __init__(self, context):

        return

    def perform(self, user_landmarks, user_image):

        return

class Keeping :
    def __init__(self, context):

        return

    def perform(self, user_landmarks, user_image):

        return

class Completing :
    def __init__(self, context):

        return

    def perform(self, user_landmarks, user_image):

        return

