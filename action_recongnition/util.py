from action import Action
import json
import math
import numpy as np
import copy
import cv2
from PIL import ImageFont, ImageDraw, Image
import cv2
import numpy as np
from numpy import unicode

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
                diff = cur - std
                sum_diff += math.pow(diff, 2)

            aver_diff = sum_diff / len(current)
        except Exception as e:
            print ('caculatePoseDifference except:{}'.format(e))

        return aver_diff
    def scaleCoordinate(self, point, shape):
        point['x'] = point['x'] * shape[1]
        point['y'] = point['y'] * shape[0]
        point['z'] = point['z'] * shape[2]

        return point

    def getAllAnglePoints(self, pose_landmarks, shape):
        angle_points = []

        for config in angle_points_config:
            points = {}
            try:
                points[K_START] = copy.deepcopy(pose_landmarks[config[0]])
                points[K_MID] = copy.deepcopy(pose_landmarks[config[1]])
                points[K_END] = copy.deepcopy(pose_landmarks[config[2]])

                if None != shape:
                    points[K_START] = self.scaleCoordinate(points[K_START], shape)
                    points[K_MID] = self.scaleCoordinate(points[K_MID], shape)
                    points[K_END] = self.scaleCoordinate(points[K_END], shape)
                angle_points.append(points)
            except Exception as e:
                points[K_START] = 0.0
                points[K_MID] = 0.0
                points[K_END] = 0.0
                angle_points.append(points)
                print ("point:{}, error:{}".format(config, e))

        return angle_points

    def cal_ang_vec(self, v1, v2):
        x = np.array(v1)
        y = np.array(v2)

        # 分别计算两个向量的模：
        l_x = np.sqrt(x.dot(x))
        l_y = np.sqrt(y.dot(y))
        #print('向量的模=', l_x, l_y)

        # 计算两个向量的点积
        dian = x.dot(y)
        #print('向量的点积=', dian)

        # 计算夹角的cos值：
        cos_ = dian / (l_x * l_y)
        #print('夹角的cos值=', cos_)

        # 求得夹角（弧度制）：
        angle_hu = np.arccos(cos_)
        #print('夹角（弧度制）=', angle_hu)

        # 转换为角度值：
        angle_d = angle_hu * 180 / np.pi
        #print('夹角=%f°' % angle_d)

        return angle_d

    def cal_ang(self, start, mid, end):
        """
        根据三点坐标计算夹角
        :param point_1: 点1坐标
        :param point_2: 点2坐标
        :param point_3: 点3坐标
        :return: 返回任意角的夹角值，这里只是返回点2的夹角
        """
        angle_d = 0
        try:
            # v1 is your firsr vector
            # v2 is your second vector
            v1 = [start['x'] - mid['x'], start['y'] - mid['y'], start['z'] - mid['z']]
            v2 = [end['x'] - mid['x'], end['y'] - mid['y'], end['z'] - mid['z']]
            #v1 = [start['x'] - mid['x'], start['y'] - mid['y']]
            #v2 = [end['x'] - mid['x'], end['y'] - mid['y']]
            angle_d = int (self.cal_ang_vec(v1, v2))

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
    def debug_anle(self, angle_points, angles, image):
        try:
            if len(image) < 1:
                return

            idx = 0
            for angle in angles:
                text = '{}'.format( int(angle))
                point = (int(angle_points[idx][K_MID]['x']), int(angle_points[idx][K_MID]['y']))
                cv2.putText(image, text, point, cv2.FONT_HERSHEY_PLAIN, 2.0, (0, 0, 255), 2)
                idx += 1
        except Exception as e :
            print ('debug_angle:{}'.format(e))

    def debug_coodiante2vec(self, point):
        vec = (int(point['x']), int(point['y']))

        return vec

    def debug_one_angle(self, point, angle, image):
        start = self.debug_coodiante2vec(point[K_START])
        mid = self.debug_coodiante2vec(point[K_MID])
        end = self.debug_coodiante2vec(point[K_END])

        cv2.putText(image, 'start', start, cv2.FONT_HERSHEY_PLAIN, 2.0, (0, 0, 255), 2)
        cv2.putText(image, 'mid:{}'.format(angle), mid, cv2.FONT_HERSHEY_PLAIN, 2.0, (0, 0, 255), 2)
        cv2.putText(image, 'end', end, cv2.FONT_HERSHEY_PLAIN, 2.0, (0, 0, 255), 2)

    def translateLandmarks(self, pose_landmarks, shape , image ):

        angle_points = self.getAllAnglePoints(pose_landmarks, shape)

        angles = self.caculateAngles(angle_points)

        self.debug_anle(angle_points, angles, image)

        idx = 2
        #self.debug_one_angle(angle_points[idx], int(angles[idx]), image)

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

    def paint_chinese_opencv(self, im, chinese, pos, color):
        #return im

        img_PIL = Image.fromarray(cv2.cvtColor(im, cv2.COLOR_BGR2RGB))
        font = ImageFont.truetype('NotoSansCJK-Bold.ttc', 25)
        fillColor = (255, 0, 0)  # (255,0,0)
        position = pos  # (100,100)
        if not isinstance(chinese, unicode):
            chinese = chinese.decode('utf-8')
        draw = ImageDraw.Draw(img_PIL)
        draw.text(position, chinese, font=font, fill=fillColor)

        img = cv2.cvtColor(np.asarray(img_PIL), cv2.COLOR_RGB2BGR)
        return img

    #def getAction(self, actions, name):
Util = Util()