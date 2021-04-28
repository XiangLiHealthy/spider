import cv2
import mediapipe as mp
from google.protobuf.json_format import MessageToDict
import json

mp_drawing = mp.solutions.drawing_utils
mp_pose = mp.solutions.pose

import os
import glob

key_points = [16, 14, 12, 11, 13, 15, 23, 25, 27, 28, 26, 24]

class VideoConfigMaker :
  def __init__(self):
    self.video = None

    return

  def get_files(self) :
    path = './sample'
    file_list = glob.glob("./video/*.mp4")

    return file_list

  def getAllImages(self, file):
    cap = cv2.VideoCapture(file)
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

      image = cv2.cvtColor(cv2.flip(image, 1), cv2.COLOR_BGR2RGB)
      # To improve performance, optionally mark the image as not writeable to
      # pass by reference.
      image.flags.writeable = False

    return

  def filterLandmarks(self, landmarks):
      try:
        # for point in key_points :
        #   if landmarks[point]['visibility'] < 0.5 :
        #     return None

        return landmarks
      except Exception as e :
        print (e)

      return None

  def get_landmarks(self, file) :

    video_landmarks = []
    try:
      # For static images:
      with mp_pose.Pose(
              static_image_mode=False,
              min_detection_confidence=0.1,
              #min_tracking_confidence=0.5
      ) as pose:
          cap = cv2.VideoCapture(file)
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

            #image = cv2.cvtColor(cv2.flip(image, 1), cv2.COLOR_BGR2RGB)
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

            one_pose = {}

            landmarks = MessageToDict(results.pose_landmarks)
            landmarks = self.filterLandmarks(landmarks['landmark'])
            if None == landmarks :
              continue

            one_pose['landmarks'] = landmarks
            one_pose['frame_num'] = frame_num
            one_pose['keep_time'] = 0
            one_pose['tips'] = 'please heading forward'
            one_pose['time_pose_ms'] = cap.get(0)

            shape = {}
            image_height, image_width, depth = image.shape
            shape['width'] = image_width
            shape['height'] = image_height
            shape['depth'] = depth

            one_pose['shape'] = shape

            video_landmarks.append(one_pose)

    except Exception as e :
      print ('get landmarks error:{}'.format(e))

    return video_landmarks

  def get_complete_info(self, landmarks, file) :
    try:
      cap = cv2.VideoCapture(file)
      time = 0.0

      if cap.isOpened():
        frame_num = cap.get(7)
        fps = cap.get(5)
        time = frame_num / fps

      action = {}
      # calculate total time
      action['action_time'] = time

      # set action name
      (path, filename) = os.path.split(file)
      action['name']    = filename
      action['en_name'] = filename
      action['mode']    = 'full_body'
      action['pose']    = landmarks
      action['video_file'] = filename

    except Exception as e :
      print ('get completed info failed:{}'.format(e))

    return action

  def save(self, j_action) :
    try:
      config_file = './action_model.json'
      config = []
      # if os.path.exists(config_file) :
      #   with open(config_file, 'r') as f :
      #     config = json.load(f)

      for action in j_action :
        config.append(action)

      with open(config_file, "w") as outfile:
        json.dump(config, outfile, sort_keys=True, indent=2)

    except Exception as e :
      print ('save error :{}'.format(e))

    return

  def perform(self):
    try:
      action_videos = self.get_files()
      acitons = []
      for file in action_videos :
        j_landmarks = self.get_landmarks(file)
        j_action = self.get_complete_info(j_landmarks, file)
        if len(j_landmarks) > 0 :
          acitons.append(j_action)

      self.save(acitons)
    except Exception as e:
      print('perform config make error:{}'.format(e))

    return

if __name__ == '__main__':
  maker = VideoConfigMaker()
  maker.perform()