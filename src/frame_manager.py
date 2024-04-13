import cv2
import numpy as np
from skimage.exposure import rescale_intensity, equalize_hist

import lib.ht301_hacklib

from helper import addTimestamp

def capture_frames(frames, camera_id):
    # Тут поки що захардкодив теплак
    if camera_id == 2:
        cap = lib.ht301_hacklib.HT301(camera_id)
    else:
        cap = cv2.VideoCapture(camera_id)

    while True:
        ret, frame = cap.read()
        if ret:
            # Тут поки що захардкодив теплак
            if camera_id == 2:
                frame = frame.astype(np.float32)

                frame = rescale_intensity(
                    equalize_hist(frame), in_range="image", out_range=(0, 255)
                ).astype(np.uint8)

                frame = cv2.applyColorMap(frame, cv2.COLORMAP_INFERNO)

            addTimestamp(frame)

            frames[camera_id] = frame
