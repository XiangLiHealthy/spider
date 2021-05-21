import requests
import chardet
import time
import  urllib3
import  ssl
from uri_def import *
from requests.packages.urllib3.exceptions import InsecureRequestWarning

import cv2
import mediapipe as mp
from google.protobuf.json_format import MessageToDict
import json
from util import Util
import numpy as np

mp_drawing = mp.solutions.drawing_utils
mp_pose = mp.solutions.pose

import os
import glob

tmp = urllib3.disable_warnings(InsecureRequestWarning)

URL_HTTPS = 'https://127.0.0.1:{}'.format(LISTEN_PORT)
ssl._create_default_https_context = ssl._create_stdlib_context
s = requests.Session()

def test_post(url, data):
    try:
        r = s.post(url, json = data, verify = False)
        if r.status_code == 200 :
            r.encoding = chardet.detect(r.content)["encoding"]
            return r.text
    except Exception as e :
        print ('tets_post url:{}, error:{}'.format(url, e))
    return None

def https_get(url, data):
    try:
        print ('https_get url:{}'.format(url))

        r = s.get(url, verify=False)
        if r.status_code == 200:
            r.encoding = chardet.detect(r.content)["encoding"]
            return r.text
    except Exception as e :
        print (e)

    return None

def test_https_post(url, data):

    return

class VideoManager :
    def __init__(self):
        self.path_ = ''
        self.cap_ = None

    def get_image(self, path):
        if path != self.path_:
            self.cap_ = cv2.VideoCapture(path)
            self.path_ = path

        image = None
        if self.cap_.isOpened():
            success, image = self.cap_.read()
            if not success:
                print("Ignoring empty camera frame.")
                self.cap_.release()
                self.path_ = ''

        #image = cv2.flip(image, 1)

        return image


class TestRecongV1_0_0:
    def __init__(self):
        self.user_video_ = VideoManager()
        self.teacher_video_ = VideoManager()

    def set_action(self, action_name, user_id, count, solution):
        data = {
            "user_id": user_id,
            "action_name": action_name,
            "task_count": count,
            "solution": solution
        }

        last = time.perf_counter()
        r = test_post(URL_HTTPS + URI_SET_ACTION, data)
        print(r)
        print('set_action use time:{}'.format(time.perf_counter() - last))

        return

    def draw_result(self, str_response, image, fact_count, action_name):
        try:
            image = cv2.resize(image, (1280, 1440))

            if str_response is None:
                print('action recong response is None')
                return -1, image

            response = json.loads(str_response)
            result = response['result']
            desc = response['desc']
            data = response['data']
            count = data['count']
            score = data['score']
            tips = data['error_tip']
            keep_time = data['time_keep']
            state = data['state']
            diff = data['diff']
            idx = data['idx']

            x = 10
            y = 60
            text = 'count:{}/{}, socre:{}, diff:{},idx:{}'.format(count,
                    fact_count, int(score), int(diff), idx)

            #image = cv2.resize(image, (1280, 1440))
            cv2.putText(image, text, (x, y), cv2.FONT_HERSHEY_PLAIN, 4.0,
                        (0, 0, 255), 4)


            return count, image
        except Exception as e:
            print('draw result except:{}'.format(e))

        return -1, image

    def upload_landmarks(self, user_id, path, play_times, action_name, need_count, teacher_path) :
        video_landmarks = []
        try:
            # For static images:
            with mp_pose.Pose(
                    static_image_mode=False,
                    min_detection_confidence=0.1,
                    # min_tracking_confidence=0.5
            ) as pose:
                cap = cv2.VideoCapture(path)
                count = 0
                while cap.isOpened():
                    success, image = cap.read()
                    if not success:
                        print("Ignoring empty camera frame.")
                        cap.release()
                        break

                    # image = cv2.cvtColor(cv2.flip(image, 1), cv2.COLOR_BGR2RGB)
                    # To improve performance, optionally mark the image as not writeable to
                    # pass by reference.
                    #image = cv2.flip(image, 1)
                    image.flags.writeable = False

                    results = pose.process(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))

                    r = None
                    count = 0
                    if results.pose_landmarks is not None:
                        image.flags.writeable = True
                        mp_drawing.draw_landmarks(image, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)

                        landmarks = MessageToDict(results.pose_landmarks)
                        print ('landmark count:{}'.format(len(landmarks['landmark'])))
                        data = {
                            'user_id' : user_id,
                            'landmarks' : landmarks['landmark']
                        }

                        last = time.perf_counter()
                        r = test_post(URL_HTTPS + URI_UPLOAD_LANDMARKS, data)
                        print(r)
                        print('upload landmarks use time:{}'.format(time.perf_counter() - last))

                        Util.translateLandmarks(landmarks['landmark'], image.shape, image)

                    count, image = self.draw_result(r, image, play_times, action_name)

                    teacher_image = self.teacher_video_.get_image(teacher_path)
                    height, width, _ = image.shape
                    teacher_image = cv2.resize(teacher_image, (width, height))
                    image = np.hstack((teacher_image, image))

                    cv2.imshow('get_landmarks', image)
                    if cv2.waitKey(5) & 0xFF == 27:
                        break

                    if count >= need_count:
                        break



        except Exception as e:
            print('get landmarks error:{}'.format(e))

        return count

    def finish_action(self, user_id):
        data = {
            'user_id' :  user_id
        }

        last = time.perf_counter()
        r = test_post(URL_HTTPS + URI_FINISH, data)
        print (r)
        print('finish use time:{}'.format(time.perf_counter() - last))

        return


    def perform(self):
        id = time.perf_counter()
        tasks = [
            {'user_id' : int(id), 'action_name' : 'ce_ping_ju.mp4',
             'file_path' : '../action_recongnition/video/ce_ping_ju.mp4', 'train_count' : 5},
            # {'user_id': int(id), 'action_name': 'qian_hou_bai_shou2.mp4',
            #  'file_path': '../action_recongnition/video/qian_hou_bai_shou2.mp4', 'train_count': 5},
            {'user_id': int(id), 'action_name': 'ce_tai_shou.mp4',
             'file_path': '../action_recongnition/video/ce_tai_shou.mp4', 'train_count': 5},
            # {'user_id': int(id), 'action_name': 'shenzhan.mp4',
            #  'file_path': '../action_recongnition/video/shenzhan.mp4', 'train_count': 5},
            {'user_id': int(id), 'action_name': 'tai_shou.mp4',
             'file_path': '../action_recongnition/video/tai_shou.mp4', 'train_count': 5},
            # {'user_id': int(id), 'action_name': 'ti_ce.mp4',
            #  'file_path': '../action_recongnition/video/ti_ce.mp4', 'train_count': 5},
        ]
        url = "rtsp://admin:admin@192.168.17.62:8554/live"
        url = "rtsp://admin:admin@192.168.1.195:8554/live"
        url = 0

        while True:
            for task in tasks:
                self.set_action(task['action_name'], task['user_id'], task['train_count'], 'train')

                play_times = 0
                count = 0
                while count < task['train_count']:
                    ret = self.upload_landmarks(task['user_id'], url,
                                                play_times, task['action_name'], task['train_count'], task['file_path'])

                    # ret = self.upload_landmarks(task['user_id'], task['file_path'],
                    #                             play_times, task['action_name'], task['train_count'])


                    count = ret
                    play_times += 1

                self.finish_action(task['user_id'])

        return None

if __name__ == '__main__':
    test_v_1_0_0 = TestRecongV1_0_0()
    test_v_1_0_0.perform()