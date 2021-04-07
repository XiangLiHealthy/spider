from action import Action
from util import Util
from google.protobuf.json_format import Parse
import json
import dict_to_protobuf as d2p
import cv2

POSE_THRESHOLD = 300


class ActionGuide:
    def __init__(self, context):
        self.m_current_action = Action()
        self.m_pose_angle_index = 0
        self.m_context = context

        return

    def setCurrentAction(self, action):
        self.m_current_action = action

        return
    def draw_landmark(self, landmarks, teacher_shape):
        current_shape = self.m_context.m_image.shape
        x_scale = teacher_shape['width'] / current_shape[1] * current_shape[1]
        y_scale = teacher_shape['height'] / current_shape[0] * current_shape[0]
        for landmark in landmarks :
            x = landmark['x'] * x_scale
            y = landmark['y'] * y_scale
            cv2.circle(self.m_context.m_image, (int(x), int(y)), 5, (255, 0, 0))

        for joint in joint_lines :
            start = landmarks[joint[0]]
            end = landmarks[joint[1]]

            start_x = int(start['x'] * x_scale)
            start_y = int(start['y'] * y_scale)
            end_x = int(end['x'] * x_scale)
            end_y = int(end['y'] * y_scale)

            cv2.line(self.m_context.m_image, (start_x, start_y), (end_x, end_y), (0, 0, 255), 15)

        return

    def guideAction(self, pose, image):
        #查看用户姿态角度是否做到当前角度，如果没做到就绘制当前角度，否则绘制下一个姿态

        try:
            #get current index angles
            angles = self.m_current_action.m_pose_angles
            if len(angles) == 0 :
                return

            self.m_pose_angle_index = self.m_current_action.m_current_pose_idx
            local_pose = angles[self.m_pose_angle_index]

            #cucalute angle difference
            diff = Util.caculatePoseDifference(pose, local_pose['angles'])

            # set current pose index
            if diff < POSE_THRESHOLD:
                self.m_pose_angle_index += 1
            if self.m_pose_angle_index >= len(self.m_current_action.m_pose_angles) :
                self.m_pose_angle_index = 0

            #draw current index landmarks
            landmarks = self.m_current_action.m_teacher_pose['pose'][self.m_pose_angle_index]['landmarks']
            shape = self.m_current_action.m_teacher_pose['pose'][self.m_pose_angle_index]['shape']
            #d2p.parse_list(landmarks, protobuf_landmarks.landmarks )

            #self.m_context.mp_drawing.draw_landmarks(
                #image, protobuf_landmarks, self.m_context.mp_pose.POSE_CONNECTIONS)

            Util.draw_landmark(landmarks, image, shape)
        except Exception as e :
            print ('guideAction:{}'.format(e))

        return image

