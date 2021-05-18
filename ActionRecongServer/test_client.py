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

mp_drawing = mp.solutions.drawing_utils
mp_pose = mp.solutions.pose

import os
import glob

# tmp = urllib3.disable_warnings(InsecureRequestWarning)

URL_HTTPS = 'http://127.0.0.1:9999'
#ssl._create_default_https_context = ssl._create_stdlib_context
#s = requests.Session()

def test_post(url, data):
    try:
        user_agent = "Mozilla/4.0 (compatible;MSIE 5.5; Windows NT)"
        # 伪装成浏览器
        headers = {"User-Agent": user_agent}
        r = requests.post(url, data ={'data' : 132})
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

def set_action(action_name, user_id) :
    data = {
        'user_id' :  user_id,
        'action_name' : action_name,
        'task_count' : 5,
        'soluation' : 'train'
    }

    last = time.perf_counter()
    r = test_post(URL_HTTPS + URI_SET_ACTION, data)
    print (r)
    print('set_action use time:{}'.format(time.perf_counter() - last))

    return

def upload_landmarks(user_id, path) :
    video_landmarks = []
    try:
        # For static images:
        with mp_pose.Pose(
                static_image_mode=False,
                min_detection_confidence=0.1,
                # min_tracking_confidence=0.5
        ) as pose:
            cap = cv2.VideoCapture(path)
            image = None
            results = None

            images = {}
            while cap.isOpened():
                frame_num = cap.get(1)
                success, image = cap.read()
                if not success:
                    print("Ignoring empty camera frame.")
                    cap.release()
                    break

                # image = cv2.cvtColor(cv2.flip(image, 1), cv2.COLOR_BGR2RGB)
                # To improve performance, optionally mark the image as not writeable to
                # pass by reference.
                image = cv2.flip(image, 1)
                image.flags.writeable = False

                results = pose.process(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))

                if not results.pose_landmarks:
                    continue

                image.flags.writeable = True
                mp_drawing.draw_landmarks(image, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)

                cv2.imshow('get_landmarks', image)
                if cv2.waitKey(5) & 0xFF == 27:
                    break

                landmarks = MessageToDict(results.pose_landmarks)
                data = {
                    'user_id' : user_id,
                    'landmarks' : landmarks['landmark']
                }

                last = time.perf_counter()
                r = test_post(URL_HTTPS + URI_UPLOAD_LANDMARKS, data)
                print(r)
                print('upload landmarks use time:{}'.format(time.perf_counter() - last))

    except Exception as e:
        print('get landmarks error:{}'.format(e))

    return None

    return

def finish_action(user_id):
    data = {
        'user_id' :  user_id
    }

    last = time.perf_counter()
    r = test_post(URL_HTTPS + URI_FINISH, data)
    print (r)
    print('finish use time:{}'.format(time.perf_counter() - last))

    return

# if __name__ == '__main__':
#     user_id = 123
#     action_name = 'ce_ping_ju.mp4'
#     file_path = '../action_recongnition/video/ce_ping_ju.mp4'
#
#     while True :
#         set_action(action_name, user_id)
#
#         upload_landmarks(user_id, file_path)
#
#         finish_action(user_id)



myobj = {'somekey': 'somevalue'}

x = requests.post(URL_HTTPS + "/test_post", data = myobj)

print(x.text)