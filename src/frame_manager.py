import cv2
from multiprocessing import Manager

def capture_frames(camera_id, frames):
    cap = cv2.VideoCapture(camera_id)
    while True:
        ret, frame = cap.read()
        if ret:
            frames[camera_id] = frame
