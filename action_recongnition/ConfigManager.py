import json
import action
import time
from datetime import date
from action import Action
from util import Util
from evaluation_state import EvaluationState
from util import angles_idx
import datetime

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
        self.teacher_angle_0 = []

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
            self.SHOW_SPLIT = 'split'
            self.SHOW_COVER = 'cover'
            self.model_file_ = './action_model.json'
            self.record_file_  = './action_record.json'
            self.task_file_ = './action_task.json'
            self.model_config_ = ''
            self.record_config_ = ''
            self.task_config_ = ''

            self.loadRecord()
            self.loadActionModel()
            self.load_task()
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

        return None

    def load_task(self):
        with open(self.task_file_, 'r') as f:
            self.task_config_ = json.load(f)

        return

    def getEvaluationState(self):
        try:
            actions = self.task_config_['evaluation']
            print ('get evaluation action cuunt : {}'.format(len(actions)))

            for action in actions :
                last_date = action['last_date']
                cycle = action['cycle']
                print ('{}, evaluation date:{}, cycle:{}'.format(action['action_name'], action['last_date'], action['cycle']))
                if '' == last_date :
                    return self.EVALUATION_NEED

                cur_date = date.today()
                period = cur_date - date.fromisoformat(last_date)
                if period.days >= cycle :
                    return self.EVALUATION_NEED
        except Exception as e :
            print ('getEvaluationState error:{}'.format(e))

        return self.EVALUATION_FINISH

    def setEvaluationState(self, name, state):
        if EvaluationState.COMPLETE != state :
            return

        try:
            actions = self.task_config_['evaluation']
            for action in actions:
                if name == action['action_name'] :
                    action['last_date'] = datetime.datetime.now().strftime('%Y-%m-%d')
                    with open(self.task_file_, "w") as outfile:
                        json.dump(self.task_config_, outfile, sort_keys=True, indent=2)
                    break
        except Exception as e :
            print ('setEvaluationState error:{}'.format(e))

        return

    def getTrainActions(self):
        train_actions = None
        try:
            train_actions = self.task_config_['train_task']
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

        return self.TEACH_NEED

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

            task = g_config.get_task_by_name(action.m_name)
            if None != task :
                action.angles_range = task['angles_range']
        except Exception as e :
            print ('createAction error :{}'.format(e))

        return action

    def getEvaluationTasks(self):
        try:
            all_tasks = self.task_config_['evaluation']
            undone_tasks = []

            for task in all_tasks :
                last_date = task['last_date']
                cycle = task['cycle']

                current_date = date.fromisoformat(last_date)
                period = date.today() - current_date
                if period.days >= cycle :
                    tmp = EvaluationTask()
                    tmp.j_config_ = task
                    undone_tasks.append(tmp)
        except Exception as e :
            print ('getEvaluationTasks except :{}'.format(e))

        return undone_tasks

    def get_report_path(self):

        return './report'

    def get_evaluation_records(self, name):
        try:
            if None == name :
                return self.task_config_['evaluation']

            for evaluation in self.task_config_['evaluation'] :
                if name == evaluation['action_name'] :
                    results = evaluation['results']
                    return results
        except Exception as e :
            print ('get_evaluation_records except:{}'.format(e))

        return None

    def get_idx_by_part(self, name):
        return angles_idx[name]

    def save_task_config(self):
        try:
            with open(self.task_file_, "w") as outfile:
                json.dump(self.task_config_, outfile, sort_keys=True, indent=2)
        except Exception as e :
            print ('save_task_config except :{}'.format(e))

        return

    def save_task(self, tasks):
        try:
            self.task_config_['train_task'] = tasks

            self.save_task_config()
        except Exception as e :
            print ('save_task except :{}'.format(e))

        return

    def get_task_config(self):

        return self.task_config_

    def save_evaluation_results(self, new_result):
        try:
            evaluations = self.task_config_['evaluation']
            for evaluation in evaluations :
                if evaluation['action_name'] == new_result['action_name'] :
                    evaluation['results'] = new_result['results']
        except Exception as e :
            print ('save_evaluation_results except:{}'.format(e))

        return

    def get_task_by_name(self, name):
        try:
            train_tasks = self.task_config_['train_task']
            for task in train_tasks :
                if name == task['action_name'] :
                    return task

        except Exception as e :
            print ('get_task_by_name except :{}'.format(e))

        return None

    def get_show_mode(self):

        return self.task_config_['user_config']['show_mode']
g_config = ConfigManager()

