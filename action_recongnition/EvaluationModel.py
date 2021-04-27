from evaluation_state import EvaluationState
from ConfigManager import g_config

from EvaluationStateMachine import Prepare
from EvaluationStateMachine import Teaching
from EvaluationStateMachine import Evaluating
from EvaluationStateMachine import Keeping
from EvaluationStateMachine import CreateReport
from EvaluationStateMachine import NextAction

import cv2
from VideoManager import VideoManager
from action import Action
from datetime import date
import time

EVALUATION_WIN_NAME = 'evaluation'

class EvaluationModel :
    def __init__(self):
        try:
            self.tasks_ = []
            self.tast_idx_ = 0
            self.current_task_ = None
            self.state_ = EvaluationState.INIT
            self.callbacks_ = {
                EvaluationState.TEACHING : Teaching(self),
                EvaluationState.PREPARE : Prepare(self),
                EvaluationState.EVALUATING : Evaluating(self),
                EvaluationState.KEEP_POSE : Keeping(self),
                EvaluationState.NEXT : NextAction(self),
                EvaluationState.CREATE_REPORT : CreateReport(self)
            }
            self.evaluation_image_ = None
            self.video_manager_ = VideoManager()
            self.teacher_action_ = Action()
            self.evaluation_result_ = []
        except Exception as e:
            print ('EvaluationModel except:{}'.format(e))

        return

    def initTask(self):
        try:
            if len(self.tasks_) == 0 :
                # 1. get evaluation tasks
                self.tasks_ = g_config.getEvaluationTasks()
                if len(self.tasks_) == 0 :
                    self.state_ = EvaluationState.COMPLETE
                    return

                self.task_idx_ = 0
                self.state_ = EvaluationState.TEACHING
                self.current_task_ = self.tasks_[self.task_idx_]

                self.teacher_action_ = g_config.getTeacherActions(self.current_task_.j_config_['action_name'])
        except Exception as e :
            print ('initTask exception :{}'.format(e))

        return self.state_

    def release(self):
        self.video_manager_.release()
        self.teacher_action_ = None
        self.tasks_.clear()
        self.current_task_ = None
        self.evaluation_result_ = None

        return

    def perform(self, user_landmarks, user_image):
        try:
            if EvaluationState.COMPLETE == self.state_ :
                return self.state_

            # set current task
            last_time = time.perf_counter()
            if self.initTask() == EvaluationState.COMPLETE :
                return self.state_
            print ('init task time:{}'.format(time.perf_counter() - last_time))

            # 2.perform by task state
            last_time = time.perf_counter()
            self.state_ = self.callbacks_[self.state_].perform(user_landmarks, user_image)
            print ('state:{}, callback time:{}'.format(self.state_, time.perf_counter() - last_time))

            last_time = time.perf_counter()
            # 4.create evaluation report
            if EvaluationState.COMPLETE == self.state_ :
                self.release()
                #cv2.destroyWindow(EVALUATION_WIN_NAME)
            # else:
            #     cv2.imshow(EVALUATION_WIN_NAME, self.evaluation_image_)
            print ('show evaluation image time :{}'.format(time.perf_counter() - last_time))

        except Exception as e :
            print ('perform evaluate failed'.format(e))

        return self.state_


