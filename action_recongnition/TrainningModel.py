from ConfigManager import g_config
from VideoManager import VideoManager
from action import  Action
from util import Util
import cv2
import time
import math

THRESHOLD = 300
ANGLE_ERROR_THRESHOLD = 10

class TrainningModel :
    def __init__(self):
        self.m_teacher_actions = []
        self.m_current_action = Action()
        self.m_action_idx = 0
        self.pose_idx_ = 0
        self.m_train_task = []
        self.count = 0
        self.video_manager_ = VideoManager()
        self.teacher_frame_ = None
        self.keep_time_start_ = None
        self.keep_time_state_ = 'finish'

        self.point_ = {}
        self.point_['x'] = 40
        self.point_['y'] = 40

        return

    def setCurrentAction(self):
        if self.m_aciton_idx >= len(self.m_teacher_actions) :
            return g_config.TRAIN_OK

        task = self.m_train_task[self.m_action_idx]
        if self.count >= task['count'] :
            self.m_action_idx += 1
            self.count = 0

        return

    def trainActions(self, user_landmarks, user_image):
        self.train_task = g_config.getTrainActions()
        self.m_teacher_actions.clear()

        for task in self.m_train_task :
            teacher_action = g_config.getTeacherActions(task['action_name'])
            self.m_teacher_actions.append(teacher_action)

        if g_config.TRAIN_OK == self.setCurrentAction() :
            return g_config.TRAIN_OK

        self.teach()

        error_angles = self.recong(user_landmarks, user_image)

        self.point(error_angles, user_landmarks, user_image)

        self.count()

        self.score()

        return

    def recong(self, user_landmarks, user_image):
        error_angles = []

        # match current teacher pose with user pose
        user_angles = Util.translateLandmarks(user_landmarks, user_image.shape, user_image)
        teacher_angles = self.m_current_action.m_pose_angles[self.pose_idx_]
        diff = Util.caculatePoseDifference(user_angles, teacher_angles)
        if diff > THRESHOLD :
            for idx in range(len(user_angles)) :
                error_angle = user_angles[idx] - teacher_angles[idx]
                error_angles.append(error_angle)

        return error_angles

    def teach(self):
        teach_state = g_config.getTeachState()
        if g_config.TEACH_FINISH == teach_state :
            return

        video_path = self.m_current_action.video_paht_
        self.video_manager_.setVideo(video_path)

        # get action video frame by index
        frame_idx = self.m_current_action.m_teacher_pose[self.pose_idx_]['frame_num']
        self.teacher_frame_ = self.video_manager_.getFrameByIdx(frame_idx)

        return

    def point(self, error_angles, user_landmarks, user_image):
        self.point_['x'] = 40
        self.point_['y'] = 40

        # 1.pose config  tips
        self.pointConfigTips(user_image)

        # 2. keep time
        self.pointKeepTime(user_image)

        # 3. error angle tips
        self.pointErrorAngle(error_angles, user_landmarks, user_image)

        # 4. error speed tips
        self.pointSpeed(user_landmarks, user_image)

        self.pointStaticsAngles(error_angles, user_image)

        return

    def count(self):

        return

    def score(self):

        return

    def pointConfigTips(self, user_image):
        teacher_pose = self.m_current_action.m_teacher_pose[self.pose_idx_]
        config_tip = teacher_pose['tips']

        if '' != config_tip :
            cv2.putText(user_image, config_tip, (self.point_['x'], self.point_['y']), cv2.FONT_HERSHEY_PLAIN, 2.0, (0, 0, 255), 2)
            self.point_['y'] += 20

        return config_tip

    def pointKeepTime(self, user_image):
        # there must be not error ,it will keep time
        teacher_pose = self.m_current_action.m_teacher_pose[self.pose_idx_]
        need_keep_time = teacher_pose['keep_time']

        if self.keep_time_state_ == 'finish' :
            self.keep_time_state_ = 'keeping'
            self.keep_time_start_ = time.perf_counter()

        current_time = time.perf_counter()
        kept_time = current_time - self.keep_time_start_
        if kept_time > need_keep_time :
            self.keep_time_state_ = 'finish'
        else:
            reciporacal = need_keep_time - kept_time
            text = 'reciporacal:{}'.format(reciporacal)
            cv2.putText(user_image, text, (self.point_['x'], self.point_['y']), cv2.FONT_HERSHEY_PLAIN, 2.0,
                        (0, 0, 255), 2)
            self.point_['y'] += 20

        return

    def pointErrorAngle(self, error_angles, user_landmarks, user_image):
        if len(error_angles) == 0 :
            return

        angle_points = Util.getAllAnglePoints(user_landmarks, user_image.shape)
        for idx in range(0, len(angle_points)) :
            if math.fabs(error_angles[idx]) > ANGLE_ERROR_THRESHOLD :
                point = angle_points[idx][1]
                text = 'error:{}'.format(int(error_angles[idx]))
                cv2.putText(user_image, text, (point['x'], point['y']), cv2.FONT_HERSHEY_PLAIN, 2.0,
                            (0, 0, 255), 2)

        return

    def pointSpeed(self, user_landmarks, user_image):

        return

    def pointStaticsAngles(self, error_angles):

        return

