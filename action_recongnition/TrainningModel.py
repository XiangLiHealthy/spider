from ConfigManager import g_config
from VideoManager import VideoManager
from action import  Action
from util import Util
import cv2
import time
import math
from action_counter import ActionCounter
from TTS import TTS
from TTS import runTTSProcess
import math

ANGLE_ERROR_THRESHOLD = 10
KEEP_FINISHED = 'finish'
KEEP_DOING = 'doing'
TIP_CONFIDENCE = 0.7
MIN_CHANGE_ANGLE = 3

class TrainningModel :
    def __init__(self):
        try:
            self.m_teacher_actions = []
            self.m_current_action = Action()
            self.m_action_idx = 0
            self.pose_idx_ = 0
            self.m_train_task = []
            self.video_manager_ = VideoManager()
            self.teacher_frame_ = None
            self.last_frame_idx = -1
            self.keep_time_start_ = 0
            self.keep_time_state_ = KEEP_FINISHED

            self.point_ = {}
            self.point_['x'] = 40
            self.point_['y'] = 40
            self.LINE_HEIGHT = 25
            self.tts_ = TTS()
            self.kept_time_ = 0

            runTTSProcess(self.tts_)
        except Exception as e :
            print ('TrainningModel __init__ error:{}'.format(e))
        return

    def show_result(self):
        self.point_['x'] = 40
        self.point_['y'] = 40
        text = ''
        cv2.putText(self.teacher_frame_, 'train tasks has finished', (self.point_['x'], self.point_['y']), cv2.FONT_HERSHEY_PLAIN, 2.0,
                    (0, 0, 255), 2)
        self.point_['y'] += self.LINE_HEIGHT

        for action in self.m_teacher_actions:
            text = '{}, count:{}, socre:80'.format(action.m_name, action.count)
            cv2.putText(self.teacher_frame_, text, (self.point_['x'], self.point_['y']), cv2.FONT_HERSHEY_PLAIN, 2.0,
                    (0, 0, 255), 2)
            self.point_['y'] += self.LINE_HEIGHT

        return

    def setCurrentAction(self):
        try:
            while True:
                if self.m_action_idx >= len(self.m_teacher_actions) :
                    self.show_result()
                    return g_config.TRAIN_OK

                task = self.m_train_task[self.m_action_idx]

                if self.m_current_action.count >= task['count'] :
                    self.m_action_idx += 1
                    self.m_current_action = self.m_teacher_actions[self.m_action_idx]
                else :
                    self.m_current_action = self.m_teacher_actions[self.m_action_idx]
                    break

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
            error_angles = Util.calculateAngleDiff(user_landmarks, user_image, self.m_current_action.m_teacher_pose[self.pose_idx_]['landmarks'], self.teacher_frame_)

            print('5.point')
            self.point(error_angles, user_landmarks, user_image)

            print('6.conting')
            self.counting(error_angles, user_image)

            print('7.score')
            self.score()

            # print('8.show teacher image')
            # image = cv2.resize(self.teacher_frame_, (1280, 1440))
            # cv2.imshow('teacher', image)
            #self.tts_.run()
        except Exception as e :
            print ('trainActions error:{}'.format(e))

        return

    def initTrainTask(self):
        try:
            if (len(self.m_teacher_actions) > 0) :
                print ('train task:{}/{}'.format(self.m_action_idx + 1, len(self.m_teacher_actions)))
                return

            self.m_train_task = g_config.getTrainActions()
            #self.m_teacher_actions.clear()

            for task in self.m_train_task:
                teacher_action = g_config.getTeacherActions(task['action_name'])
                if None == teacher_action:
                    print('there is not aciton name:{}'.format(task['action_name']))
                    continue

                self.m_teacher_actions.append(teacher_action)

            print ('get train task count : {}'.format(len(self.m_teacher_actions)))
        except Exception as e :
            print ('initTrainTask error ;{}'.format(e))

        return

    def teach(self):
        try:
            teach_state = g_config.getTeachState()
            print ('teach state is:{}'.format(teach_state))
            if g_config.TEACH_FINISH == teach_state :
                return

            video_path = self.m_current_action.video_path
            self.video_manager_.setVideo(video_path)
            print('set video path:{}'.format(video_path))

            # get action video frame by index
            frame_idx = self.m_current_action.m_teacher_pose[self.pose_idx_]['frame_num']
            if self.last_frame_idx != frame_idx :
                image = self.video_manager_.getFrameByIdx(frame_idx)
                self.teacher_frame_ = image #cv2.flip(image, 1)
                self.last_frame_idx = frame_idx

            print ('get video idx:{}'.format(frame_idx))
        except Exception as e :
            print ('teach error:{}'.format(e))

        return

    def point(self, error_angles, user_landmarks, user_image):
        try:
            self.point_['x'] = 40
            self.point_['y'] = 20

            # 1.pose config  tips
            self.pointConfigTips(user_image)

            # 2. keep time
            self.pointKeepTime(error_angles, user_image)

            # 3. error angle tips
            Util.pointErrorAngle(error_angles, user_landmarks, user_image)

            # 4. error speed tips
            self.pointSpeed(user_landmarks, user_image)

            self.pointStaticsAngles(error_angles, user_image)

            #self.pointUserPositions(user_landmarks, user_image)

        except Exception as e :
            print ('point error:{}'.format(e))

        return

    def pointUserPositions(self, user_landmarks, user_image):
        #self.pointUserPosition(user_landmarks[27], user_landmarks[28], user_image, "please back off")
        if user_landmarks[27]['visibility'] < TIP_CONFIDENCE and user_landmarks[28]['visibility'] < TIP_CONFIDENCE :
            text = 'please back off'
            cv2.putText(user_image, text, (self.point_['x'], self.point_['y']), cv2.FONT_HERSHEY_PLAIN, 2.0,
                        (0, 0, 255), 2)
            self.point_['y'] += self.LINE_HEIGHT

        #self.pointUserPosition(user_landmarks[16], user_landmarks[28], user_image, "please to the right")
        if (user_landmarks[16]['visibility'] < TIP_CONFIDENCE and user_landmarks[15]['visibility'] > TIP_CONFIDENCE ) \
                or (user_landmarks[28]['visibility'] < TIP_CONFIDENCE and user_landmarks[27]['visibility'] > TIP_CONFIDENCE):
            text = 'please to the right'
            cv2.putText(user_image, text, (self.point_['x'], self.point_['y']), cv2.FONT_HERSHEY_PLAIN, 2.0,
                        (0, 0, 255), 2)
            self.point_['y'] += self.LINE_HEIGHT

        #self.pointUserPosition(user_landmarks[27], user_landmarks[15], user_image, "plese to the left")
        if (user_landmarks[15]['visibility'] < TIP_CONFIDENCE and user_landmarks[16]['visibility'] > TIP_CONFIDENCE ) or \
                (user_landmarks[27]['visibility'] < TIP_CONFIDENCE and user_landmarks[28]['visibility'] > TIP_CONFIDENCE):
            text = 'please to the left'
            cv2.putText(user_image, text, (self.point_['x'], self.point_['y']), cv2.FONT_HERSHEY_PLAIN, 2.0,
                        (0, 0, 255), 2)
            self.point_['y'] += self.LINE_HEIGHT

        return

    def is_angle_in_range(self, range, teacher_angles):
        for angle_range in range:
            angle_idx = g_config.get_idx_by_part(angle_range['name'])
            angle = teacher_angles[angle_idx]
            if angle_range['start_angle'] < angle_range['end_angle']:
                if angle > angle_range['end_angle']:
                    return False
            else:
                if angle <= angle_range['start_angle']:
                    return False

        return True

    def is_enogh_change(self, ranges, next_idx):
        last_angles = self.m_current_action.m_pose_angles[self.pose_idx_]['angles']
        next_angles = self.m_current_action.m_pose_angles[next_idx]['angles']
        for range in ranges :
            angle_idx = g_config.get_idx_by_part(range['name'])
            if math.fabs(last_angles[angle_idx] - next_angles[angle_idx]) > MIN_CHANGE_ANGLE :
                return True

        return False

    def get_next_idx(self):
        next_idx = 0
        try:
        # get all anggle range for current task
        # test next pose weather ok, or next
            for next_idx in range(self.pose_idx_ + 1, len(self.m_current_action.m_teacher_pose)) :
                if not self.is_enogh_change(self.m_current_action.angles_range, next_idx) :
                    continue

                flag = self.is_angle_in_range(self.m_current_action.angles_range,
                             self.m_current_action.m_pose_angles[next_idx]['angles'])
                if flag == True :
                    break

            if next_idx + 1 == len(self.m_current_action.m_teacher_pose):
                self.m_current_action.count += 1
                self.pose_idx_ = 0
                next_idx = 0
        except Exception as e :
            print ('train get_next_idx except:{}'.format(e))

        return next_idx

    def counting(self, error_angles, user_image):
        try:
            next_idx = 0

            # are there error angles,
            if len(error_angles) > 0 :
                if KEEP_DOING == self.keep_time_state_ :
                    if g_config.TEACH_FINISH == g_config.getTeachState() :
                        next_idx = self.get_next_idx()
                    else:
                        next_idx = self.pose_idx_
                else:
                    next_idx = self.pose_idx_
            else:
                if KEEP_DOING == self.keep_time_state_ :
                    next_idx = self.pose_idx_
                else :
                    next_idx = self.get_next_idx()

            print ('error angles count:{}, keep state:{}, teach state:{}, next_idx:{}, pose count:{}'.format(len(error_angles),
                 self.keep_time_state_, g_config.getTeachState(), next_idx, len(self.m_current_action.m_pose_angles)))

            if next_idx != self.pose_idx_ :
                self.keep_time_state_ = KEEP_FINISHED
                # record actual keep time

            self.pose_idx_ = next_idx

            text = '{},count:{}'.format(self.m_current_action.m_en_name, self.m_current_action.count)
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
                self.point_['y'] += self.LINE_HEIGHT

                self.tts_.say(config_tip)
        except Exception as e:
            print ('pointConfigTips error:{}'.format(e))

        return config_tip

    def pointKeepTime(self, error_angles, user_image):
        try:
            # there must be not error ,it will keep time
            teacher_pose = self.m_current_action.m_teacher_pose[self.pose_idx_]
            need_keep_time = teacher_pose['keep_time']

            if self.keep_time_state_ == KEEP_FINISHED :
                self.keep_time_state_ = KEEP_DOING
                self.keep_time_start_ = time.perf_counter()


            if len(error_angles) > 0 :
                self.keep_time_start_ = time.perf_counter() - self.kept_time_

            current_time = time.perf_counter()
            self.kept_time_ = current_time - self.keep_time_start_
            if self.kept_time_ > need_keep_time :
                self.keep_time_state_ = KEEP_FINISHED
            else:
                reciporacal = int(need_keep_time - self.kept_time_)
                text = 'keep pose {} second'.format(reciporacal)
                cv2.putText(user_image, text, (self.point_['x'], self.point_['y']), cv2.FONT_HERSHEY_PLAIN, 2.0,
                            (0, 0, 255), 2)
                self.point_['y'] += self.LINE_HEIGHT

                self.tts_.say(text)

            print ('pose idx:{}, need keep:{}, kept time:{}'.format(self.pose_idx_, need_keep_time, self.kept_time_))
        except Exception as e :
            print ('pointKeepTime error:{}'.format(e))

        return

    def pointSpeed(self, user_landmarks, user_image):

        return

    def pointStaticsAngles(self, error_angles, user_iamge):

        return

