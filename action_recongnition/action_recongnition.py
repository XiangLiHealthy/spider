import cv2
import mediapipe as mp
from google.protobuf.json_format import MessageToDict
from numpy import unicode

from util import Util
from action_guide import ActionGuide
from action_classification import ActionClassification
from action_counter import ActionCounter
from action_score import ActionScore
from possible_action import PossibleAction

from PIL import ImageFont, ImageDraw, Image
import cv2
import numpy as np

class ActionRecongnition:
    def __init__(self):
        self.m_guide_name = ''
        self.m_guide_flag = False

        self.m_classifier = ActionClassification()
        self.m_counter = ActionCounter()
        self.m_score = ActionScore()
        self.m_guider = ActionGuide(self)

        actions = Util.loadAcitonDB()
        self.m_classifier.setActionSet(actions)

        self.m_possible_action = PossibleAction()
        self.m_current_count = 0
        self.m_current_score = 0

        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_pose = mp.solutions.pose

        return

    def recong_aciton(self, pose):
        try:
            # recong action
            self.m_possible_action = self.m_classifier.classify(pose)
            if None == self.m_possible_action:
                return
            # print(self.m_possible_action.m_name)

            # action count
            self.m_current_count = self.m_counter.addAction(self.m_possible_action)
            # print('count{} : {}'.format(self.m_possible_action.m_name, self.m_current_count))

            # score
            self.m_curent_score = self.m_score.getScore(self.m_possible_action)
            print('name:{}, index:{}, score:{}'.format(self.m_possible_action.m_name, self.m_current_count,
                                                       self.m_current_score))
        except Exception as e:
            print('recong_aciton:{}'.format(e))

        return

    def paint_chinese_opencv(self, im, chinese, pos, color):
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

    def draw_result(self, image):
        try:
            #draw action name ,count, score
            if None == self.m_possible_action:
                return image

            name = self.m_possible_action.m_name
            count = self.m_counter.m_counter
            score = self.m_curent_score

            text = '{} : {}, score: {}'.format(name, count, score)

            #cv2.putText(image, text, (40, 50), cv2.FONT_HERSHEY_PLAIN, 2.0, (0, 0, 255), 2)
            image = self.paint_chinese_opencv(image, text, (40, 50), (0, 0, 255))
        except Exception as e :
            print ("draw_result:{}".format(e))

        return image

    def guide_action(self, pose, protobuf_landmarks, image):
        # guide action if set aciton name
        if '' != self.m_guide_name:
            action = self.m_classifier.getActionByName(self.m_guide_name)
            self.m_guider.setCurrentAction(action)
        elif None == self.m_possible_action:
            return
        else:
            self.m_guider.setCurrentAction(self.m_possible_action)

        #find action that need guide
        image = self.m_guider.guideAction(pose, protobuf_landmarks, image)

        return image

    def recong(self, protobuf_landmarks, image):
        if protobuf_landmarks == None:
            return image


        landmarks = MessageToDict(protobuf_landmarks)
        pose_angle = Util.translateLandmarks(landmarks['landmark'], image)

        self.recong_aciton(pose_angle)

        self.guide_action(pose_angle, protobuf_landmarks, image)

        image = self.draw_result(image)

        return image

    def startup(self):
        # url = "rtsp://admin:admin@192.168.17.62:8554/live"
        url = "rtsp://admin:admin@192.168.18.143:8554/live"
        url = "./sample/action.mp4"

        # For webcam input:
        cap = cv2.VideoCapture(url)
        with self.mp_pose.Pose(
                min_detection_confidence=0.5,
                min_tracking_confidence=0.5) as pose:
            while cap.isOpened():
                success, image = cap.read()
                if not success:
                    print("Ignoring empty camera frame.")
                    # If loading a video, use 'break' instead of 'continue'.
                    continue

                # Flip the image horizontally for a later selfie-view display, and convert
                # the BGR image to RGB.
                image = cv2.cvtColor(cv2.flip(image, 1), cv2.COLOR_BGR2RGB)
                # To improve performance, optionally mark the image as not writeable to
                # pass by reference.
                image.flags.writeable = False
                results = pose.process(image)

                image.flags.writeable = True
                image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
                #image_tmp = image
                image = self.recong(results.pose_landmarks, image)
                # Draw the pose annotation on the image.
                self.mp_drawing.draw_landmarks(
                    image, results.pose_landmarks, self.mp_pose.POSE_CONNECTIONS,
                    mp.solutions.drawing_utils.DrawingSpec(color=(255, 0, 0)))
                cv2.imshow('MediaPipe Pose', image)
                if cv2.waitKey(5) & 0xFF == 27:
                    break

            cap.release()

        return

    def stop(self):

        return