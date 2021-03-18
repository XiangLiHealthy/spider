from action import Action
import json
import math
import numpy as np

angle_points_config = [
    [28, 26, 24],#right knee
    [26, 24, 12],#right hip
    [24, 12, 14],#right shoulder
    [12, 14, 16],#right elbow
    [27, 25, 23],#left knee
    [25, 23, 11],#left hip
    [23, 11, 13],#left shoulder
    [11, 13, 15],#left elbow
]

K_START = 'start'
K_MID = 'mid'
K_END = 'end'

class Util:
    def __init__(self):
        self.m_model_path = 'action_model.json'

        return
    def caculatePoseDifference(self, current, standard):
        sum_diff = 0.0

        try:
            count = len(current)
            for idx in range(count):
                cur = current[idx]
                std = standard[idx]
                sum_diff += (cur - std) * (cur - std)

            aver_diff = sum_diff / len(current)
        except Exception as e:
            print ('caculatePoseDifference except:{}'.format(e))

        return aver_diff

    def getAllAnglePoints(self, pose_landmarks):
        angle_points = []

        for config in angle_points_config:
            points = {}
            try:
                points[K_START] = pose_landmarks[config[0]]
                points[K_MID] = pose_landmarks[config[1]]
                points[K_END] = pose_landmarks[config[2]]
                angle_points.append(points)
            except Exception as e:
                points[K_START] = 0.0
                points[K_MID] = 0.0
                points[K_END] = 0.0
                angle_points.append(points)
                print ("point:{}, error:{}".format(config, e))

        return angle_points

    def cal_ang(self, start, mid, end):
        """
        根据三点坐标计算夹角
        :param point_1: 点1坐标
        :param point_2: 点2坐标
        :param point_3: 点3坐标
        :return: 返回任意角的夹角值，这里只是返回点2的夹角
        """
        angle_d = 0.0
        try:
            # v1 is your firsr vector
            # v2 is your second vector
            v1 = [start['x'] - mid['x'], start['y'] - mid['y'], start['z'] - mid['z']]
            v2 = [end['x'] - mid['x'], start['y'] - mid['y'], start['z'] - mid['z']]
            angle = np.arccos(np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2)))
            angle_d = 2 * np.pi - angle

        except Exception as e :
            print ('cal_ang:{}'.format(e))

        return angle_d

    def caculateAngles(self, angle_points):
        angles = []
        for points in angle_points:
            try:
                angle = self.cal_ang(points[K_START], points[K_MID], points[K_END])
                angles.append(angle)
            except Exception as e:
                print ('caculateAngles:{}'.format(e) )

        return angles

    def translateLandmarks(self, pose_landmarks):
        angle_points = self.getAllAnglePoints(pose_landmarks)

        angles = self.caculateAngles(angle_points)

        return angles

    def loadAcitonDB(self):
        try:
            f = open(self.m_model_path)
            text = f.read()
            j_actions = json.loads(text)

            return j_actions
        except Exception as e:
            print ("loadAcitonDB:{}".format(e) )

        return None

    #def getAction(self, actions, name):
Util = Util()