
from ConfigManager import EvaluationTask
from ConfigManager import EvaluationState
from ConfigManager import g_config

from EvaluationStateMachine import Prepare
from EvaluationStateMachine import Teaching
from EvaluationStateMachine import Evaluating
from EvaluationStateMachine import Keeping
from EvaluationStateMachine import Completing

import cv2
from VideoManager import VideoManager
from action import Action

class EvaluationModel :
    def __init__(self):
        self.tasks_ = []
        self.tast_idx_ = 0
        self.current_task_ = EvaluationTask()
        self.state_ = EvaluationState.INIT
        self.callbacks_ = {
            EvaluationState.TEACHING : Teaching(self),
            EvaluationState.PREPARE : Prepare(self),
            EvaluationState.EVALUATING : Evaluating(self),
            EvaluationState.KEEP_POSE : Keeping(self),
            EvaluationState.COMPLETE : Completing(self)
        }
        self.evaluation_image_ = None
        self.video_manager_ = VideoManager()
        self.teacher_action_ = Action()

        return

    def initTask(self):
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

        return self.state_

    def changeTask(self, state):
        if EvaluationState.COMPLETE == state and self.task_idx_ < len(self.tasks_):
            self.task_idx_ += 1

        return

    def perform(self, user_landmarks, user_image):
        if EvaluationState.COMPLETE == self.state_ :
            return

        # set current task
        if self.initTask() == EvaluationState.COMPLETE :
            return

        # 2.perform by task state
        self.state_ = self.callbacks_[self.state_].perform(user_landmarks, user_image)

        # 3.change action if complete
        self.changeTask(self.state_)

        cv2.imshow('evaluation', self.evaluation_image_)

        return


