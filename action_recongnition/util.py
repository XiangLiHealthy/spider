from action import Action
import json
import math

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
            for cur, std in current, standard:
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

    def cal_ang(self, point_1, point_2, point_3):
        """
        根据三点坐标计算夹角
        :param point_1: 点1坐标
        :param point_2: 点2坐标
        :param point_3: 点3坐标
        :return: 返回任意角的夹角值，这里只是返回点2的夹角
        """
        try:
            a = math.sqrt((point_2[0] - point_3[0]) * (point_2[0] - point_3[0]) + (point_2[1] - point_3[1]) * (
                        point_2[1] - point_3[1]))
            b = math.sqrt((point_1[0] - point_3[0]) * (point_1[0] - point_3[0]) + (point_1[1] - point_3[1]) * (
                        point_1[1] - point_3[1]))
            c = math.sqrt((point_1[0] - point_2[0]) * (point_1[0] - point_2[0]) + (point_1[1] - point_2[1]) * (
                        point_1[1] - point_2[1]))
            A = math.degrees(math.acos((a * a - b * b - c * c) / (-2 * b * c)))
            B = math.degrees(math.acos((b * b - a * a - c * c) / (-2 * a * c)))
            C = math.degrees(math.acos((c * c - a * a - b * b) / (-2 * a * b)))
        except Exception as e :
            print ('cal_ang:{}'.format(e))

        return B

    def caculateAngles(self, angle_points):
        angles = []
        for points in angle_points:
            try:
                angle = self.cal_ang(points[K_START], points[K_MID], points[K_END])
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
