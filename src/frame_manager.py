import cv2
from multiprocessing import Manager
from helper import addTimestamp

def capture_frames(frames, camera_id):
    cap = cv2.VideoCapture(camera_id)
    while True:
        ret, frame = cap.read()
        if ret:
            addTimestamp(frame)

            frames[camera_id] = frame
