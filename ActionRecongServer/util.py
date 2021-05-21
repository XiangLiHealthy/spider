import json
import math
import numpy as np
import copy
import cv2
from PIL import ImageFont, ImageDraw, Image
import cv2
import numpy as np
from numpy import unicode

ANGLE_ERROR_THRESHOLD = 5
THRESHOLD = 100
TIP_CONFIDENCE = 0.7

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

angles_idx = {
    "right_knee" : 0,
    "right_hip" : 1,
    "right_shoulder" : 2,
    "right_elbow" : 3,
    "left_knee" : 4,
    "left_hip" : 5,
    "left_shoulder" : 6,
    "left_elbow" : 7
}

joint_lines = [
    [1, 2],
    [2, 3],
    [3, 7],
    [0, 1],
    [0, 4],
    [4, 5],
    [5, 6],
    [6, 8],
    [10, 9],
    [18, 20],
    [20, 16],
    [18, 16],
    [16, 22],
    [16, 14],
    [14, 12],
    [12, 11],
    [11, 13],
    [13, 15],
    [15, 21],
    [15, 19],
    [15, 17],
    [12, 24],
    [24, 26],
    [24, 23],
    [26, 28],
    [28, 32],
    [32, 30],
    [30, 28],
    [11, 23],
    [23, 25],
    [25, 27],
    [27, 31],
    [31, 29],
    [27, 29]
]

K_START = 'start'
K_MID = 'mid'
K_END = 'end'

class Util:
    def __init__(self):
        self.m_model_path = 'action_model.json'
        return

    def get_idx_by_part(self, name):
        return angles_idx[name]

    def caculate_diff_with_parts(self, teacher_angles, user_angles, part_idxs):
        sum_diff = 0
        for idx in part_idxs :
            diff = teacher_angles[idx] - user_angles[idx]
            square = pow(diff, 2)
            sum_diff += square

        return sum_diff / len(part_idxs)

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
            # v1 = [start['x'] - mid['x'], start['y'] - mid['y'], start['z'] - mid['z']]
            # v2 = [end['x'] - mid['x'], end['y'] - mid['y'], end['z'] - mid['z']]
            v1 = [start['x'] - mid['x'], start['y'] - mid['y']]
            v2 = [end['x'] - mid['x'], end['y'] - mid['y']]
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

    def debug_landmarks(self, landmarks, shape, image):
        try:
            for landmark in landmarks:
                x = landmark['x'] * shape[1]
                y = landmark['y'] * shape[0]
                cv2.circle(image, (int(x), int(y)), 5, (255, 0, 0))

            for joint in joint_lines:
                start = landmarks[joint[0]]
                end = landmarks[joint[1]]

                start_x = int(start['x'] * shape[1])
                start_y = int(start['y'] * shape[0])
                end_x = int(end['x'] * shape[1])
                end_y = int(end['y'] * shape[0])

                cv2.line(image, (start_x, start_y), (end_x, end_y), (0, 0, 255), 2)
        except Exception as e :
            #print ('debug_landmarks error:{}'.format(e))
            a = 1

        return

    def translateLandmarks(self, pose_landmarks, shape = None , image = None ):

        angle_points = self.getAllAnglePoints(pose_landmarks, shape)

        angles = self.caculateAngles(angle_points)

        #self.debug_anle(angle_points, angles, image)
        #self.debug_landmarks(pose_landmarks, shape, image)

        idx = 2
        #self.debug_one_angle(angle_points[idx], int(angles[idx]), image)
        self.debug_anle(angle_points, angles, image)

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
    def draw_landmark(self, landmarks, m_context, teacher_shape):
        current_shape = m_context.shape
        x_scale = teacher_shape['width'] / current_shape[1] * current_shape[1]
        y_scale = teacher_shape['height'] / current_shape[0] * current_shape[0]
        for landmark in landmarks :
            x = landmark['x'] * x_scale
            y = landmark['y'] * y_scale
            cv2.circle(m_context, (int(x), int(y)), 5, (255, 0, 0))

        for joint in joint_lines :
            start = landmarks[joint[0]]
            end = landmarks[joint[1]]

            start_x = int(start['x'] * x_scale)
            start_y = int(start['y'] * y_scale)
            end_x = int(end['x'] * x_scale)
            end_y = int(end['y'] * y_scale)

            cv2.line(m_context, (start_x, start_y), (end_x, end_y), (255, 0, 0), 15)

        return

    def calculateAngleDiff(self, user_landmarks, user_image, teacher_landmarks, teacher_image):
        try:
            error_angles = []

            # match current teacher pose with user pose
            user_angles = Util.translateLandmarks(user_landmarks, user_image.shape, user_image)
            teacher_angles = Util.translateLandmarks(teacher_landmarks, teacher_image.shape, teacher_image)
            diff = Util.caculatePoseDifference(user_angles, teacher_angles)
            if diff > THRESHOLD :
                for idx in range(0, len(user_angles)) :
                    error_angle = user_angles[idx] - teacher_angles[idx]
                    error_angles.append(error_angle)

            print('user_angles:{}'.format(user_angles))
            print('teacher_angles:{}'.format(teacher_angles))
            print('diff:{},diff angles:{}'.format(diff, error_angles))
        except Exception as e :
            print ('recong error :{}'.format(e))

        return error_angles

    def pointErrorAngle(self, error_angles, user_landmarks, user_image):
        try:
            print ('error angles:{}, threshold : {}'.format(error_angles, THRESHOLD))

            if len(error_angles) == 0 :
                return

            angle_points = Util.getAllAnglePoints(user_landmarks, user_image.shape)
            for idx in range(0, len(angle_points)) :
                if math.fabs(error_angles[idx]) > ANGLE_ERROR_THRESHOLD :
                    point = angle_points[idx]['mid']
                    text = 'error:{}'.format(int(error_angles[idx]))
                    cv2.putText(user_image, text, (int(point['x'] - 40), int(point['y'])), cv2.FONT_HERSHEY_PLAIN, 2.0,
                                (0, 0, 255), 2)
                    #self.tts_.say(text)
        except Exception as e :
            print ('pointErrorAngle error:{}'.format(e))

        return

    def pointUserPositions(self, user_landmarks, user_image):
        point_ = {}
        point_['x'] = 40
        point_['y'] = 40
        LINE_HEIGHT = 20
        error = False

        #self.pointUserPosition(user_landmarks[27], user_landmarks[28], user_image, "please back off")
        if user_landmarks[27]['visibility'] < TIP_CONFIDENCE and user_landmarks[28]['visibility'] < TIP_CONFIDENCE :
            text = 'please back off'
            cv2.putText(user_image, text, (point_['x'], point_['y']), cv2.FONT_HERSHEY_PLAIN, 2.0,
                        (0, 0, 255), 2)
            point_['y'] += LINE_HEIGHT
            error = True

        #self.pointUserPosition(user_landmarks[16], user_landmarks[28], user_image, "please to the right")
        if (user_landmarks[16]['visibility'] < TIP_CONFIDENCE and user_landmarks[15]['visibility'] > TIP_CONFIDENCE ) \
                or (user_landmarks[28]['visibility'] < TIP_CONFIDENCE and user_landmarks[27]['visibility'] > TIP_CONFIDENCE):
            text = 'please to the right'
            cv2.putText(user_image, text, (point_['x'], point_['y']), cv2.FONT_HERSHEY_PLAIN, 2.0,
                        (0, 0, 255), 2)
            point_['y'] += LINE_HEIGHT
            error = True

        #self.pointUserPosition(user_landmarks[27], user_landmarks[15], user_image, "plese to the left")
        if (user_landmarks[15]['visibility'] < TIP_CONFIDENCE and user_landmarks[16]['visibility'] > TIP_CONFIDENCE ) or \
                (user_landmarks[27]['visibility'] < TIP_CONFIDENCE and user_landmarks[28]['visibility'] > TIP_CONFIDENCE):
            text = 'please to the left'
            cv2.putText(user_image, text, (point_['x'], point_['y']), cv2.FONT_HERSHEY_PLAIN, 2.0,
                        (0, 0, 255), 2)
            point_['y'] += LINE_HEIGHT
            error = True

        return error

    def get_part_idxs(self, parts):
        idxs = []
        for part in parts :
            idx = self.get_idx_by_part(part)
            idxs.append(idx)

        return idxs

    #def getAction(self, actions, name):
Util = Util()