import cv2
import mediapipe as mp
from google.protobuf.json_format import MessageToDict
import json

mp_drawing = mp.solutions.drawing_utils
mp_pose = mp.solutions.pose

import os
import glob

path = './sample'
file_list = glob.glob("./sample/*.jpg")

# For static images:
with mp_pose.Pose(
    static_image_mode=True, min_detection_confidence=0.5) as pose:

  for idx, file in enumerate(file_list):
    image = cv2.imread(file)
    image_height, image_width, depth = image.shape
    # Convert the BGR image to RGB before processing.
    results = pose.process(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))

    if not results.pose_landmarks:
      continue

    (path, filename) = os.path.split(file)
    file_name = '{}/{}.json'.format(path, filename)

    landmarks = MessageToDict(results.pose_landmarks)

    pose_angle = {}
    pose_angle['landmarks'] = landmarks['landmark']

    shape = {}
    shape['width'] = image_width
    shape['height'] = image_height
    shape['depth'] = depth

    pose_angle['shape'] = shape
    pose_angle['keep_time'] = 0

    action = {}
    action['name'] = filename
    action['action_time'] = 7
    action['mode'] = 'upper'

    pose_angles = []
    pose_angles.append(pose_angle)
    action['pose'] = pose_angles


    with open(file_name, "w") as outfile:
        json.dump(action, outfile)

    # Draw pose landmarks on the image.
    annotated_image = image.copy()
    # Use mp_pose.UPPER_BODY_POSE_CONNECTIONS for drawing below when
    # upper_body_only is set to True.
    mp_drawing.draw_landmarks(
        annotated_image, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)
    cv2.imwrite('/tmp/annotated_image' + str(idx) + '.png', annotated_image)