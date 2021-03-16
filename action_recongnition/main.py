import cv2
import mediapipe as mp

from google.protobuf.json_format import MessageToDict

mp_drawing = mp.solutions.drawing_utils
mp_pose = mp.solutions.pose


#url = "rtsp://admin:admin@192.168.17.62:8554/live"
url = "rtsp://admin:admin@192.168.18.143:8554/live"
url = "action.mp4"

# For webcam input:
cap = cv2.VideoCapture(url)
with mp_pose.Pose(
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

    #deserilize ptotobuf
    #org = results.pose_landmarks.Deserialize()
    if results.pose_landmarks != None :
      dict_obj = MessageToDict(results.pose_landmarks)
      print (dict_obj)

    # Draw the pose annotation on the image.
    image.flags.writeable = True
    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
    mp_drawing.draw_landmarks(
        image, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)
    cv2.imshow('MediaPipe Pose', image)
    if cv2.waitKey(5) & 0xFF == 27:
      break
cap.release()
