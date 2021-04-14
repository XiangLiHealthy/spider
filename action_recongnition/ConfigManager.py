import json
import action
import time
from datetime import date
from action import Action
from util import Util
from EvaluationStateMachine import EvaluationState

class EvaluationTask:
    def __init__(self):
        self.state = EvaluationState.INIT


        self.keep_start_time = 0

        self.j_config_ = {}
        self.evaluation_landmark_ = {}
        self.evaluation_angles = []
        self.teacher_pose_idx_ = 0
        self.evaluation_image_ = None
        self.scores_ = []
        self.sychronize_scroe_ = 0.0
        self.teacher_image_ = None
        self.teacher_landmarks_ = {}

        return

class ConfigManager :
    def __init__(self):
        try:

            self.EVALUATION_NEED = 'need'
            self.EVALUATION_FINISH = 'finish'
            self.TRAIN_OK = 'ok'
            self.TRAIN_DOING = 'doing'
            self.TEACH_NEED = 'nedd'
            self.TEACH_FINISH = "finish"

            self.model_file_ = './action_model.json'
            self.record_file_  = './action_record.json'
            self.model_config_ = ''
            self.record_config_ = ''

            self.loadRecord()
            self.loadActionModel()
        except Exception as e :
            print ('config manager init error:{}'.format(e))

        return

    def loadActionModel(self):
        try:
          with open(self.model_file_, 'r') as f :
            self.model_config_ = json.load(f)

        except Exception as e :
            print ('load action model error:{}'.format(e))

    def loadRecord(self):
        try:
          with open(self.record_file_, 'r') as f :
            self.record_config_ = json.load(f)

        except Exception as e :
            print ('load action model error:{}'.format(e))

        return

    def getEvaluationState(self):
        try:
            actions = self.record_config_['evaluation']['actions']
            print ('get evaluation action cuunt : {}'.format(len(actions)))

            for action in actions :
                last_date = action['last_date']
                cycle = action['cycle']
                print ('{}, evaluation date:{}, cycle:{}'.format(action['action_name'], action['last_date'], action['cycle']))
                if '' == last_date :
                    return self.EVALUATION_NEED

                cur_date = date.today()
                period = cur_date - date.fromisoformat(last_date)
                if period.days > cycle :
                    return self.EVALUATION_NEED
        except Exception as e :
            print ('getEvaluationState error:{}'.format(e))

        return self.EVALUATION_FINISH

    def setEvaluationState(self, name, state):
        try:
            actions = self.record_config_['evaluation']['actions']
            for action in actions:
                if name == action['name'] :
                    action['last_date'] = date.isoformat()
                    with open(self.record_file_, "w") as outfile:
                        json.dump(self.record_config_, outfile, sort_keys=True, indent=2)
                    break
        except Exception as e :
            print ('setEvaluationState error:{}'.format(e))

        return

    def getTrainActions(self):
        train_actions = None
        try:
            train_actions = self.record_config_['train_task']
            records = self.record_config_['record']
        except Exception as e :
            print ('getTrainAction error:{}'.format(e))

        return train_actions

    def getTeacherActions(self, name):
        try:
            actions = self.model_config_
            for action in actions :
                if name == action['name'] :
                    return self.createAction(action)
        except Exception as e :
            print ('getTeachAcitons error:{}'.format(e))

        return None

    def getTeachState(self):
        try:
            tasks = self.getTrainActions()
            if len(tasks) > 0 :
                return self.TEACH_NEED
            else :
                return self.TEACH_FINISH
        except Exception as e :
            print ('getTeachState error:{}'.format(e))

        return

    def setTeachState(self):

        return

    def getAllActions(self):

        return

    def createAction(self, j_action):
        try:
            action = Action()
            action.m_name = j_action['name']
            action.m_en_name = j_action['en_name']
            action.m_action_time = j_action['action_time']

            action.video_path = './video/' + j_action['video_file']

            pose_angles = j_action['pose']
            if len(pose_angles) < 1 :
                return None

            for angle in pose_angles:
                joint_angle = {}
                joint_angle['keep_time'] = angle['keep_time']
                shape = [angle['shape']['height'], angle['shape']['width'], angle['shape']['depth']]
                joint_angle['angles'] = Util.translateLandmarks(angle['landmarks'], None, None)
                joint_angle['possible'] = 0
                action.m_pose_angles.append(joint_angle)

                # image = np.zeros((shape[0], shape[1], 3), np.uint8);
                # Util.draw_landmark(angle['landmarks'], image, angle['shape'])
                # Util.translateLandmarks(angle['landmarks'], shape, image)
                # cv2.imshow(j_action['en_name'], image)

            action.m_teacher_pose = j_action['pose']
            action.m_match_times = 0
            action.m_need_times = len(pose_angles)
        except Exception as e :
            print ('createAction error :{}'.format(e))

        return action

    def getEvaluationTasks(self):

        return

    def get_report_path(self):

        return './report'

    def get_evaluation_records(self, name):

        return

    def get_idx_by_part(self, part):

        return

g_config = ConfigManager()

