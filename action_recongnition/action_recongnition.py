import time
import mediapipe as mp
from google.protobuf.json_format import MessageToDict
from util import Util
from action_guide import ActionGuide
from action_classification import ActionClassification
from action_counter import ActionCounter
from action_score import ActionScore
import cv2
from recong_result import RecongResult
from ConfigManager import g_config
from EvaluationModel import EvaluationModel
from TrainningModel import TrainningModel

class ActionRecongnition:
    def __init__(self, queue, recong_queue):
        try:
            self.m_guide_name = '侧平举'
            self.m_guide_flag = False

            self.m_classifier = ActionClassification(self)
            self.m_counter = ActionCounter()
            self.m_score = ActionScore()
            self.m_guider = ActionGuide(self)

            actions = Util.loadAcitonDB()
            self.m_classifier.setActionSet(actions)

            self.m_possible_action = None
            self.m_current_count = 0
            self.m_current_score = 0

            self.mp_drawing = mp.solutions.drawing_utils
            self.mp_pose = mp.solutions.pose
            self.m_image = None
            self.m_curent_score = 0.0

            self.m_task_queue = queue
            self.m_recong_queue = recong_queue
            self.m_pose = None
            self.m_last_time = time.perf_counter()

            self.m_evaluation = EvaluationModel()
            self.m_evaluation_result = None
            self.m_train = TrainningModel()
            self.m_evaluation_state = g_config.STATE_NEED
            self.m_train_state = g_config.TRAIN_DOING

        except Exception as e :
            print ('ActionRecongnition init :{}'.format(e))
        return

    def recong_aciton(self, pose):
        try:
            # recong action
            self.m_classifier.m_image = self.m_image
            possible_action = self.m_classifier.classify(pose)
            if None == possible_action:
                return
            # print(self.m_possible_action.m_name)

            self.m_possible_action = possible_action

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

    def draw_result(self, image):
        try:
            #draw action name ,count, score
            if None == self.m_possible_action:
                return image

            name = self.m_possible_action.m_name
            count = self.m_counter.m_counter
            score = self.m_curent_score

            text = '{} : {}, score: {}'.format(name, count, score)

            #cv2.putText(image, text, (40, 40), cv2.FONT_HERSHEY_PLAIN, 2.0, (0, 0, 255), 2)
            self.m_image = Util.paint_chinese_opencv(self.m_image, text, (40, 10), (0, 0, 255))
        except Exception as e :
            print ("draw_result:{}".format(e))

        return image

    def guide_action(self, pose, image):
        # guide action if set aciton name
        if '' != self.m_guide_name:
            self.m_possible_action = self.m_classifier.getActionByName(self.m_guide_name)
            #self.m_guider.setCurrentAction(self.m_possible_action)

        if None == self.m_possible_action:
            return

        self.m_guider.setCurrentAction(self.m_possible_action)

        #find action that need guide
        self.m_guider.guideAction(pose, image)

        return image
    def getFPS(self):
        current_time = time.perf_counter()
        fps = (1 / (current_time - self.m_last_time))
        self.m_last_time = current_time

        return int(fps)
    def evaluate(self, user_landmarks, user_image):
        try:
            state = g_config.getEvaluationState()
            print ('evaluation state is : {}'.format(state))
            if (state == g_config.EVALUATION_FINISH):
                return

            if 'success' != self.m_evaluation.perform(user_landmarks, user_image):
                print('evaluate action failed')

            g_config.setEvaluationState(g_config.STATE_FINISH)
        except Exception as e :
            print ('evaluate error:{}'.format(e))

        return

    def train(self, user_landmarks, user_image):
        try:
            train_state = g_config.getTeachState()
            print('train state is : {}'.format(train_state))

            if train_state == g_config.TRAIN_OK :

                return

            self.m_train_state = self.m_train.trainActions(user_landmarks, user_image)
        except Exception as e :
            print ('train error:{}'.format(e))

        return

    def freeStyleRecong(self, landmarks, image):
        try:
            if g_config.getTeachState() == g_config.TRAIN_DOING :
                return

            self.m_image = image
            pose_angle = Util.translateLandmarks(landmarks, image.shape, image)

            self.recong_aciton(pose_angle)

            self.guide_action(pose_angle, image)

            self.draw_result(image)
        except Exception as e :
            print ('freeStyleREcong error:{}'.format(e))

        return image

    def fetchFrameThread(self):
        url = "rtsp://admin:admin@192.168.17.62:8554/live"
        #url = "rtsp://admin:admin@192.168.18.143:8554/live"
        url = "./sample/action.mp4"

        try:
            # For webcam input:
            cap = cv2.VideoCapture(url)
            while cap.isOpened():
                success, image = cap.read()
                if not success:
                    print("Ignoring empty camera frame.")
                    # If loading a video, use 'break' instead of 'continue'.
                    cap.release()
                    cap = cv2.VideoCapture(url)
                    continue

                #cv2.imshow('camera', image)
                #if cv2.waitKey(5) & 0xFF == 27:
                #    break


                print('----receive frame----fps:{}---------'.format(self.getFPS()))

                self.m_task_queue.put(image)

                #time.sleep(0.02)

            cap.release()
        except Exception as e :
            print("fetchFrameThread:{}".format(e))

        return

    def recongActionThread(self):
        with self.mp_pose.Pose(
                min_detection_confidence=0.5,
                min_tracking_confidence=0.5) as pose:

            while True:
                try:
                    image = self.m_task_queue.get()

                    # Flip the image horizontally for a later selfie-view display, and convert
                    # the BGR image to RGB.
                    image = cv2.cvtColor(cv2.flip(image, 1), cv2.COLOR_BGR2RGB)
                    # To improve performance, optionally mark the image as not writeable to
                    # pass by reference.
                    image.flags.writeable = False

                    #height, weight, depth = image.shape
                    #image = cv2.resize(image, (640, 480))

                    results = pose.process(image)

                    image.flags.writeable = True
                    landmarks = None
                    if None != results.pose_landmarks :
                        landmarks = MessageToDict(results.pose_landmarks)

                    self.mp_drawing.draw_landmarks(image, results.pose_landmarks, self.mp_pose.POSE_CONNECTIONS)

                    self.m_recong_queue.put(RecongResult(image, landmarks))
                    print('----recong thread----fps:{}---'.format(self.getFPS()))


                except Exception as e :
                    print ('recongActionThread:{}'.format(e))

        return

    def drawVideoThread(self):
        try:
            while True:
                print ('drawvVideoThread wait....')
                recong_result = self.m_recong_queue.get()
                print('drawvideoThread get a result')

                self.m_image = recong_result.m_image
                results = recong_result.m_result

                self.m_image = cv2.cvtColor(self.m_image, cv2.COLOR_RGB2BGR)

                #self.evaluate(results, self.m_image)
                self.train(results, self.m_image)
                #self.freeStyleRecong(results, self.m_image)

                #self.m_image = cv2.resize(self.m_image, (1440, 1080))
                fps = self.getFPS()
                fps_str = 'fps:{}'.format(fps)
                print (fps_str)
                height, width, _ = self.m_image.shape
                self.m_image = cv2.putText(self.m_image, fps_str, (width - 200, 40), cv2.FONT_HERSHEY_PLAIN, 2.0, (0, 0, 255), 2)

                self.m_image = cv2.resize(self.m_image, (1440, 1080))
                cv2.imshow('MediaPipe Pose', self.m_image)
                if cv2.waitKey(5) & 0xFF == 27:
                    break



        except Exception as e :
            print ('recongActionThread:{}'.format(e))

        return

    def singleThread(self):
        with self.mp_pose.Pose(min_detection_confidence=0.5,min_tracking_confidence=0.5) as pose:
            while True:
                try:
                    url = "rtsp://admin:admin@192.168.17.62:8554/live"
                    #url = "rtsp://admin:admin@192.168.18.143:8554/live"
                    #url = "./sample/action.mp4"

                    # For webcam input:
                    cap = cv2.VideoCapture(url)
                    while cap.isOpened():
                        success, image = cap.read()
                        if not success:
                            print("Ignoring empty camera frame.")
                            # If loading a video, use 'break' instead of 'continue'.
                            cap.release()
                            cap = cv2.VideoCapture(url)
                            continue

                        # Flip the image horizontally for a later selfie-view display, and convert
                        # the BGR image to RGB.
                        image = cv2.cvtColor(cv2.flip(image, 1), cv2.COLOR_BGR2RGB)
                        # To improve performance, optionally mark the image as not writeable to
                        # pass by reference.
                        image.flags.writeable = False

                        # height, weight, depth = image.shape
                        # image = cv2.resize(image, (640, 480))

                        results = pose.process(image)

                        image.flags.writeable = True
                        landmarks = None
                        if None != results.pose_landmarks:
                            landmarks = MessageToDict(results.pose_landmarks)

                        #self.mp_drawing.draw_landmarks(image, results.pose_landmarks, self.mp_pose.POSE_CONNECTIONS)
                        self.m_image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

                        if None != landmarks :
                            landmark = landmarks['landmark']
                            #self.evaluate(landmark, self.m_image)
                            self.train(landmark, self.m_image)
                            #self.freeStyleRecong(landmark, self.m_image)

                        #self.m_image = cv2.resize(self.m_image, (1440, 1080))
                        fps = self.getFPS()
                        fps_str = 'fps:{}'.format(fps)
                        print (fps_str)
                        height, width, _ = self.m_image.shape
                        self.m_image = cv2.putText(self.m_image, fps_str, (width - 200, 40), cv2.FONT_HERSHEY_PLAIN, 2.0, (0, 0, 255), 2)

                        self.m_image = cv2.resize(self.m_image, (1280, 1440))
                        cv2.imshow('MediaPipe Pose', self.m_image)
                        if cv2.waitKey(5) & 0xFF == 27:
                            break

                except Exception as e :
                    print ('recongActionThread:{}'.format(e))

        return
