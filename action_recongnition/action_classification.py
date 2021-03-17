from action import Action
from possible_action import PossibleAction
ANGLE_THRESHOLD = 5
RATE_THRESHOLD = 0.9

class ActionClassification:
    def __init__(self):
        self.m_actions = []
        self.m_possible_actions = []

        return
    def setActionSet(self, actions):
        self.m_actions = actions
        self.m_possible_actions.clear()

        for j_action in actions:
            action = Action()
            action.m_name = j_action['name']
            action.m_action_time = j_action['action_time']

            frame_angles = j_action['angles']
            for angle in frame_angles:
                joint_angle = {}
                joint_angle['keep_time'] = angle['keep_time']
                joint_angle['angles'] = angle['angles']
                joint_angle['diff_angles'] = []
                joint_angle['possible'] = -1
                action.m_pose_angles.append(joint_angle)
            self.m_possible_actions.append(action)

            action.m_match_times = 0
            action.m_need_times = len(frame_angles)

            self.m_possible_actions.append(action)
        return
    def caculatePoseDifference(self, current, standard):

        return
    def averDiff(self, diff_angles, current_angles):

        return
    def matchOnePose(self, action, current_pose):

        return

    def markMatchState(self, pose_angle):
        is_back = False

        # match all action by every pose angle
        action = Action()
        for action in self.m_possible_actions:
            for joint in action.m_pose_angles:
                angles = joint['angles']
                diff_angles = self.caculatePoseDifference(pose_angle, angles)
                aver_diff = self.averDiff(diff_angles, pose_angle)
                if aver_diff < ANGLE_THRESHOLD:
                    if (self.matchOnePose(action, joint) is True and is_back is False):
                        is_bakc = True
                    continue

        return is_back

    def getRecongedActions(self):

        return

    def selectBestOne(self, actions):

        return actions

    def resetAllMatchState(self):

        return

    def classify(self, pose_angle):
        #it is not time to recong if go on moving forward
        if not self.markMatchState(pose_angle):
            return None

        # check weather satifying recongnition
        actions = self.getRecongedActions()

        # if recong one action, reset all match state
        if len(actions) > 0:
            self.resetAllMatchState()

        #get the best one action
        action = self.selectBestOne(actions)

        return action