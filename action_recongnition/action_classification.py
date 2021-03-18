from action import Action
from possible_action import PossibleAction
ANGLE_THRESHOLD = 5
RATE_THRESHOLD = 0.9

class ActionClassification:
    def __init__(self):
        self.m_actions = []
        self.m_possible_actions = []
        self.m_pose_angles = []

        return
    def setActionSet(self, actions):
        self.m_actions = actions
        self.m_possible_actions.clear()

        try:
            for j_action in actions:
                action = Action()
                action.m_name = j_action['name']
                action.m_action_time = j_action['action_time']

                frame_angles = j_action['angles']
                for angle in frame_angles:
                    joint_angle = {}
                    joint_angle['keep_time'] = angle['keep_time']
                    joint_angle['angles'] = angle['angles']
                    joint_angle['possible'] = -1
                    action.m_pose_angles.append(joint_angle)
                self.m_possible_actions.append(action)

                action.m_match_times = 0
                action.m_need_times = len(frame_angles)

                self.m_possible_actions.append(action)
        except Exception as e:
            print ('setActionSet'.format(e))

        return

    def caculatePoseDifference(self, current, standard):
        sum_diff = 0.0

        try:
            for cur, std in current, standard:
                sum_diff += (cur - std) * (cur - std)

            aver_diff = sum_diff / len(current)
        except Exception as e:
            print ('caculatePoseDifference except:{}'.format(e))

        return aver_diff

    def matchOnePose(self, action, current_pose):
        #看当前姿态是否已经匹配过，已经匹配过说明是动作返回
        is_back = False

        try:
            flag = current_pose['possile']
            if 1 == flag:
                is_back = True
            else:
                current_pose['possible'] = 1
                action.m_match_times += 1
        except Exception as e:
            print ('matchOnePose'.format(e))

        return is_back

    def markMatchState(self, pose_angle):
        is_back = False

        # match all action by every pose angle
        action = Action()

        try:
            self.m_pose_angles.append(pose_angle)

            for action in self.m_possible_actions:
                for joint in action.m_pose_angles:
                    angles = joint['angles']
                    aver_diff = self.caculatePoseDifference(pose_angle, angles)
                    if aver_diff < ANGLE_THRESHOLD:
                        if (self.matchOnePose(action, joint) is True and is_back is False):
                            is_bakc = True
                        continue
        except Exception as e:
            print ('markMatchState'.format(e))

        return is_back

    def getRecongedActions(self):
        #查看所有动作匹配率是否达到确认阈值
        actions = []

        try:
            for action in self.m_actions:
                rate = action.m_match_times / action.m_need_times
                if rate >= RATE_THRESHOLD:
                    actions.append(action)
        except Exception as e:
            print ('getRecongedActions except:{}'.format(e))

        return actions

    def selectBestOne(self, actions):
        #选择所有动作中角度变化最大的一个
        max_diff = 0.0
        action = Action()

        try:
            for one in actions:
                start = one.m_pose_angles[0]

                end_pos = len(one.m_pose_angles) - 1
                end = one.m_pose_angles[end_pos]

                diff = self.caculatePoseDifference(start, end)
                if diff > max_diff:
                    action = one
                    max_diff = diff
        except Exception as e:
            print ('selectBestOne except:{}'.format(e))

        return action

    def resetAllMatchState(self):
        #将match_times和possible设置为出事状态，避免干扰下一次识别
        try:
            #动作平分完成后才能清楚这个缓存
            #self.m_pose_angles.clear()

            for action in self.m_actions:
                action.m_match_times = 0
                for angle in action.m_pose_angles:
                    angle['possible'] = 0
        except Exception as e:
            print('resetAllMatchState except:{}'.format(e))

        return

    def classify(self, pose_angle):
        #it is not time to recong if go on moving forward
        if not self.markMatchState(pose_angle):
            return None

        # check weather satifying recongnition
        actions = self.getRecongedActions()
        if len (actions) < 1:
            return None

        #get the best one action
        action = self.selectBestOne(actions)

        possible_action = PossibleAction()
        possible_action.m_action = action
        possible_action.m_pose_angles = self.m_pose_angles

        # if recong one action, reset all match state
        if len(actions) > 0:
            self.resetAllMatchState()

        return action