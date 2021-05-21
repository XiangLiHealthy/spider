import json
from copy import deepcopy
from util import Util
from uri_def import  MOVE_DIRECTION
from math import fabs

class Pose :
    def __init__(self):
        self.landmarks = []
        self.angles = []
        self.up_match = 0
        self.down_match = 0
        self.tips = ''
        self.keep_time = 0
        self.up = None
        self.down = None
        self.up_diff = 0.0
        self.down_diff = 0.0
        self.frame_num = 0
        self.revert = 0
        self.revert_diff = 0.0


        return


class ActionModel :
    def __init__(self):
        self.poses = []
        self.action_name = ''
        self.video_path = ''
        self.time = 0.0
        self.last_idx = 0
        self.last_direction = MOVE_DIRECTION.UP
        self.action_time = 0.0
        self.en_name = ''
        self.video_file = ''
        self.revert_count = 0
        self.score = 0
        self.need_count = 0
        self.count = 0
        self.focus_parts = []

        return


class ConfigManager:
    def __init__(self):
        self.teacher_model_config = '../action_recongnition/action_model.json'
        self.actions_ = []

        self.load_actions()

        return

    def load_json(self, path):
        try:
            with open(path, 'r') as f:
                return json.load(f)

        except Exception as e:
            print('load action model error:{}'.format(e))

        return None

    def get_parts_idx(self, parts):

        return

    def filter_landmarks(self, action):
        try:
            last_angles = []
            focus_parts = action['focus_parts']
            poses = action['pose']
            if len(poses) == 0 :
                return

            min_diff = 1
            last_angles = None
            parts_idx = Util.get_part_idxs(focus_parts)

            new_poses = []
            for pose in poses :
                current_angles = Util.translateLandmarks(pose['landmarks'])
                if last_angles is None :
                    last_angles = current_angles
                    continue

                valid_pose = False
                for idx in parts_idx :
                    current = current_angles[idx]
                    last = last_angles[idx]
                    diff = current - last
                    if diff > min_diff :
                        valid_pose = True
                        break

                if valid_pose is True :
                    last_angles = current_angles
                    new_poses.append(pose)

            action['pose'] = new_poses
        except Exception as e:
            print ('filter landmarks except:{}'.format(e))

        return None

    def load_actions(self):
        try:
            config = self.load_json(self.teacher_model_config)
            if None == config :
                print ('load file: {} None'.format(self.teacher_model_config))
                return None

            for action_config in config :
                action_obj = ActionModel()
                action_obj.action_name = action_config['name']
                action_obj.action_time = action_config['action_time']
                action_obj.en_name = action_config['en_name']
                action_obj.video_file = action_config['video_file']
                action_obj.focus_parts = action_config['focus_parts']

                self.filter_landmarks(action_config)

                for pose_config in action_config['pose'] :
                    pose_obj = Pose()
                    pose_obj.frame_num = pose_config['frame_num']
                    pose_obj.keep_time = pose_config['keep_time']
                    pose_obj.landmarks = pose_config['landmarks']

                    pose_obj.angles = Util.translateLandmarks(pose_obj.landmarks)
                    action_obj.poses.append(pose_obj)

                self.actions_.append(action_obj)
        except  Exception as e :
            print ('config_manaager load action except:{}'.format(e))

        return None

    def get_action_by_name(self, name):
        try:
            for action in self.actions_ :
                if name == action.action_name :
                    return deepcopy(action)
        except Exception as e :
            print ('get_action_by_name except:{}'.format(e))

        return None

g_config = ConfigManager()