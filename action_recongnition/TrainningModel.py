from ConfigManager import g_config
from VideoManager import VideoManager
from action import  Action
from util import Util
import cv2
import time
import math
from action_counter import ActionCounter
from TTS import TTS

THRESHOLD = 300
ANGLE_ERROR_THRESHOLD = 10
KEEP_FINISHED = 'finish'
KEEP_DOING = 'doing'

class TrainningModel :
    def __init__(self):
        try:
            self.m_teacher_actions = []
            self.m_current_action = Action()
            self.m_action_idx = 0
            self.pose_idx_ = 0
            self.m_train_task = []
            self.count = 0
            self.video_manager_ = VideoManager()
            self.teacher_frame_ = None
            self.keep_time_start_ = 0
            self.keep_time_state_ = KEEP_FINISHED

            self.point_ = {}
            self.point_['x'] = 40
            self.point_['y'] = 40
            self.counter_ = ActionCounter()
            self.tts_ = TTS()
        except Exception as e :
            print ('TrainningModel __init__ error:{}'.format(e))
        return

    def setCurrentAction(self):
        try:
            if self.m_aciton_idx >= len(self.m_teacher_actions) :
                return g_config.TRAIN_OK

            task = self.m_train_task[self.m_action_idx]
            if self.count >= task['count'] :
                self.m_action_idx += 1
                self.count = 0
        except Exception as e :
            print('setCurrentAction error:{}'.format(e))

        return g_config.TRAIN_DOING

    def trainActions(self, user_landmarks, user_image):
        try:
            print ('1.initTrainTask')
            self.initTrainTask()

            print ('2.setCurrentAction')
            if g_config.TRAIN_OK == self.setCurrentAction() :
                return g_config.TRAIN_OK

            print ('3.teach')
            self.teach()

            print('4.recong')
            error_angles = self.recong(user_landmarks, user_image)

            print('5.point')
            self.point(error_angles, user_landmarks, user_image)

            print('6.conting')
            self.counting(error_angles, user_image)

            print('7.score')
            self.score()

            print('8.show teacher image')
            cv2.imshow('teacher', self.teacher_frame_)
            self.tts_.run()
        except Exception as e :
            print ('trainActions error:{}'.format(e))

        return

    def initTrainTask(self):
        try:
            if (len(self.m_teacher_actions) > 0) :
                print ('train task:{}/{}'.format(self.m_action_idx + 1, len(self.m_teacher_actions)))
                return

            self.m_train_task = g_config.getTrainActions()
            self.m_teacher_actions.clear()

            for task in self.m_train_task:
                teacher_action = g_config.getTeacherActions(task['action_name'])
                if None == teacher_action:
                    print('there is not aciton name:{}'.format(task['action_name']))
                    continue

                self.m_teacher_actions.append(teacher_action)

            print ('get train task count : {}'.format(self.m_teacher_actions))
        except Exception as e :
            print ('initTrainTask error ;{}'.format(e))

        return

    def recong(self, user_landmarks, user_image):
        try:
            error_angles = []

            # match current teacher pose with user pose
            user_angles = Util.translateLandmarks(user_landmarks, user_image.shape, user_image)
            teacher_angles = Util.translateLandmarks(self.m_current_action.m_teacher_pose[self.pose_idx_], self.teacher_frame_.shape, self.teacher_frame_)
            diff = Util.caculatePoseDifference(user_angles, teacher_angles)
            if diff > THRESHOLD :
                for idx in range(0, len(user_angles)) :
                    error_angle = user_angles[idx] - teacher_angles[idx]
                    error_angles.append(error_angle)

            print('user_angles:{}'.format(user_angles))
            print('teacher_angles:{}'.format(teacher_angles))
            print('diff:{},diff angles:{}'.format(diff, error_angles))
        except Exception as e :
            print ('recong error :{}'.format(e))

        return error_angles

    def teach(self):
        try:
            teach_state = g_config.getTeachState()
            print ('teach state is:{}'.format(teach_state))
            if g_config.TEACH_FINISH == teach_state :
                return

            video_path = self.m_current_action.video_path_
            self.video_manager_.setVideo(video_path)
            print('set video path:{}'.format(video_path))

            # get action video frame by index
            frame_idx = self.m_current_action.m_teacher_pose[self.pose_idx_]['frame_num']
            self.teacher_frame_ = self.video_manager_.getFrameByIdx(frame_idx)
            print ('get video idx:{}'.format(frame_idx))
        except Exception as e :
            print ('teach error:{}'.format(e))

        return

    def point(self, error_angles, user_landmarks, user_image):
        try:
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
        except Exception as e :
            print ('point error:{}'.format(e))

        return

    def counting(self, error_angles, user_image):
        try:
            next_idx = 0

            # are there error angles,
            if len(error_angles) > 0 :
                if KEEP_DOING == self.keep_time_state_ :
                    if g_config.TEACH_FINISH == g_config.getTeachState() :
                        next_idx = self.pose_idx_ + 1
                    else:
                        next_idx = self.pose_idx_
                else:
                    next_idx = self.pose_idx_
            else:
                if KEEP_DOING == self.keep_time_state_ :
                    next_idx = self.pose_idx_
                else :
                    next_idx = self.pose_idx_ + 1

            print ('error angles count:{}, keep state:{}, teach state:{}, next_idx:{}, pose count:{}'.format(len(error_angles),
                 self.keep_time_state_, g_config.getTeachState(), next_idx, len(self.m_current_action.m_pose_angles)))

            if next_idx != self.pose_idx_ :
                self.keep_time_state_ = KEEP_FINISHED
                # record actual keep time

            if next_idx == len(self.m_current_action.m_pose_angles) :
                self.count += 1
                self.counter_.addAction(self.m_current_action.m_name)
                self.pose_idx_ = 0
            else :
                self.pose_idx_ = next_idx

            text = '{},count:{}, well done'.format(self.m_current_action.m_en_name, self.count)
            cv2.putText(user_image, text, (self.point_['x'], self.point_['y']), cv2.FONT_HERSHEY_PLAIN, 2.0,
                        (0, 0, 255), 2)
            self.point_['y'] += 20

            self.tts_.say(text)
        except Exception as e :
            print ('counting error:{}'.format(e))

        return

    def score(self):

        return

    def pointConfigTips(self, user_image):
        try:
            teacher_pose = self.m_current_action.m_teacher_pose[self.pose_idx_]
            config_tip = teacher_pose['tips']

            print('pose idx:{}. tips:{}'.format(self.pose_idx_, config_tip))

            if '' != config_tip :
                cv2.putText(user_image, config_tip, (self.point_['x'], self.point_['y']), cv2.FONT_HERSHEY_PLAIN, 2.0, (0, 0, 255), 2)
                self.point_['y'] += 20

                self.tts_.say(config_tip)
        except Exception as e:
            print ('pointConfigTips error:{}'.format(e))

        return config_tip

    def pointKeepTime(self, user_image):
        try:
            # there must be not error ,it will keep time
            teacher_pose = self.m_current_action.m_teacher_pose[self.pose_idx_]
            need_keep_time = teacher_pose['keep_time']

            if self.keep_time_state_ == KEEP_FINISHED :
                self.keep_time_state_ = KEEP_DOING
                self.keep_time_start_ = time.perf_counter()

            current_time = time.perf_counter()
            kept_time = current_time - self.keep_time_start_
            if kept_time > need_keep_time :
                self.keep_time_state_ = KEEP_FINISHED
            else:
                reciporacal = need_keep_time - kept_time
                text = 'kepp pose {} second'.format(reciporacal)
                cv2.putText(user_image, text, (self.point_['x'], self.point_['y']), cv2.FONT_HERSHEY_PLAIN, 2.0,
                            (0, 0, 255), 2)
                self.point_['y'] += 20

                self.tts_.say(text)

            print ('pose idx:{}, need keep:{}, kept time:{}'.format(self.pose_idx_, need_keep_time, kept_time))
        except Exception as e :
            print ('pointKeepTime error:{}'.format(e))

        return

    def pointErrorAngle(self, error_angles, user_landmarks, user_image):
        try:
            print ('error angles:{}, threshold : {}'.format(error_angles, THRESHOLD))

            if len(error_angles) == 0 :
                return

            angle_points = Util.getAllAnglePoints(user_landmarks, user_image.shape)
            for idx in range(0, len(angle_points)) :
                if math.fabs(error_angles[idx]) > ANGLE_ERROR_THRESHOLD :
                    point = angle_points[idx]['mid']
                    text = 'error:{}'.format(int(error_angles[idx]))
                    cv2.putText(user_image, text, (point['x'], point['y']), cv2.FONT_HERSHEY_PLAIN, 2.0,
                                (0, 0, 255), 2)
                    self.tts_.say(text)
        except Exception as e :
            print ('pointErrorAngle error:{}'.format(e))

        return

    def pointSpeed(self, user_landmarks, user_image):

        return

    def pointStaticsAngles(self, error_angles):

        return

