from action import Action
from util import Util
POSE_THRESHOLD = 5

class ActionGuide:
    def __init__(self, context):
        self.m_current_action = Action()
        self.m_pose_angle_index = 0
        self.m_context = context

        return

    def setCurrentAction(self, action):
        self.m_current_action = action

        return

    def guideAction(self, pose, image):
        #查看用户姿态角度是否做到当前角度，如果没做到就绘制当前角度，否则绘制下一个姿态

        try:
            #get current index angles
            angles = self.m_current_action.m_pose_angles
            local_pose = angles[self.m_current_action]

            #cucalute angle difference
            diff = Util.caculatePoseDifference(pose, local_pose)

            # set current pose index
            self.m_pose_angle_index += 1
            if self.m_pose_angle_index >= len(self.m_current_action.m_pose_angles) :
                self.m_pose_angle_index = 0

            #draw current index landmarks
            landmarks = self.m_current_action.m_pose_landmark[self.m_pose_angle_index]
            self.m_context.mp_drawing.draw_landmarks(
                image, landmarks, self.m_context.mp_pose.POSE_CONNECTIONS)
        except Exception as e :
            print ('guideAction:{}'.format(e))

        return image

