from action import Action
from possible_action import PossibleAction
from util import Util
import cv2
import numpy as np

ANGLE_THRESHOLD = 500
RATE_THRESHOLD = 0.9

class ActionClassification:
    def __init__(self, context):
        self.m_action_config = []
        self.m_action_queue = []
        self.m_pose_angles = []
        self.m_context = context


        return
    def setActionSet(self, actions):
        self.m_action_config = actions
        self.m_action_queue.clear()

        try:
            for j_action in actions:
                action = Action()
                action.m_name = j_action['name']
                action.m_en_name = j_action['en_name']
                action.m_action_time = j_action['action_time']

                pose_angles = j_action['pose']
                for angle in pose_angles:
                    joint_angle = {}
                    joint_angle['keep_time'] = angle['keep_time']
                    shape = [angle['shape']['height'], angle['shape']['width'], angle['shape']['depth']]
                    joint_angle['angles'] = Util.translateLandmarks( angle['landmarks'], shape, None)
                    joint_angle['possible'] = 0
                    action.m_pose_angles.append(joint_angle)


                    # image = np.zeros((shape[0], shape[1], 3), np.uint8);
                    # Util.draw_landmark(angle['landmarks'], image, angle['shape'])
                    # Util.translateLandmarks(angle['landmarks'], shape, image)
                    # cv2.imshow(j_action['en_name'], image)

                action.m_teacher_pose = j_action
                action.m_match_times = 0
                action.m_need_times = len(pose_angles)

                self.m_action_queue.append(action)
        except Exception as e:
            print ('setActionSet'.format(e))

        return


    def getActionByName(self, name):
        for action in self.m_action_queue :
            if name == action.m_name :
                return action

        print ('there is not action name :{}'.format(name))
        return None

    def matchOnePose(self, action, current_pose):
        #看当前姿态是否已经匹配过，已经匹配过说明是动作返回
        is_back = False

        try:
            flag = current_pose['possible']
            if 1 == flag:
                is_back = True
            else:
                current_pose['possible'] = 1
                action.m_match_times += 1
        except Exception as e:
            print ('matchOnePose'.format(e))

        return is_back

    def debugAngles(self, texts):
        try:
            height = 100
            for text in texts:
                #self.m_context.m_image = Util.paint_chinese_opencv(self.m_context.m_image, text, (50, height), (0, 0, 255))
                cv2.putText(self.m_context.m_image, text, (50, height), cv2.FONT_HERSHEY_PLAIN, 2.0, (0, 0, 255), 2)
                height += 50
        except Exception as e :
            print ('debugAngles:{}'.format(e))

        return

    def markMatchState(self, pose_angle):
        is_back = False

        # match all action by every pose angle
        try:
            self.m_pose_angles.append(pose_angle)

            debug_acitions_angle = []
            debug_acitions_angle.append(str(pose_angle))

            for action in self.m_action_queue:

                # find min angle difference
                idx = 0
                min_diff = 1000000
                min_idx = -1
                min_pose = None
                for one_pose in action.m_pose_angles:
                    standard = one_pose['angles']
                    aver_diff = Util.caculatePoseDifference(pose_angle, standard)
                    if aver_diff < min_diff:
                        min_diff = aver_diff
                        min_idx = idx
                        min_pose = one_pose
                        #print ('min_diff:{}, min_idx:{}'.format(min_diff, min_idx))
                    idx += 1

                # it is time finish a ction when return the first pose angle
                if min_diff < ANGLE_THRESHOLD:
                    print ('name:{}, diff:{}, threshold:{}'.format(action.m_name, aver_diff, ANGLE_THRESHOLD))
                    tmp = self.matchOnePose(action, min_pose)
                    if (tmp is True and is_back is False and 0 == min_idx):
                        is_back = True
                        print ('is_back:True')

                action.m_current_pose_idx = min_idx
                debug_acitions_angle.append( '{},diff:{}'.format(action.m_en_name, min_diff))

            self.debugAngles(debug_acitions_angle)

        except Exception as e:
            print ('markMatchState'.format(e))

        return is_back

    def getRecongedActions(self):
        #查看所有动作匹配率是否达到确认阈值
        actions = []

        try:
            for action in self.m_action_queue:
                rate = action.m_match_times / action.m_need_times
                print ('name:{}, rate:{}, standard:{}'.format(action.m_name, rate, RATE_THRESHOLD))
                if rate >= RATE_THRESHOLD:
                    actions.append(action)
        except Exception as e:
            print ('getRecongedActions except:{}'.format(e))

        return actions

    def selectBestOne(self, actions):
        #选择所有动作中角度变化最大的一个
        max_diff = -1000000
        action = Action()

        try:
            for one in actions:
                start = one.m_pose_angles[0]

                end_pos = len(one.m_pose_angles) - 1
                end = one.m_pose_angles[end_pos]

                diff = Util.caculatePoseDifference(start['angles'], end['angles'])
                if diff > max_diff:
                    action = one
                    max_diff = diff

                print("select name:{}, diff:{}".format(one.m_name, diff))
        except Exception as e:
            print ('selectBestOne except:{}'.format(e))

        print ('best name:{}'.format(action.m_name))
        return action

    def resetAllMatchState(self):
        #print ('resetAllMatchState')
        #将match_times和possible设置为出事状态，避免干扰下一次识别
        try:
            #动作平分完成后才能清楚这个缓存
            #self.m_pose_angles.clear()

            for action in self.m_action_queue:
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