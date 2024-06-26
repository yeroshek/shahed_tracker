import cv2
import datetime
import os
import shutil

def addTimestamp(frame):
    if frame is None:
        return

    # Get current time
    now = datetime.datetime.now()
    current_time = now.strftime("%Y-%m-%d %H:%M:%S")

    # Get frame dimensions
    height = frame.shape[0]
    width = frame.shape[1]

    # Set font, scale, color, and thickness
    font = cv2.FONT_HERSHEY_SIMPLEX
    if width > 400:
        font_scale = 0.5
    else:
        font_scale = 0.3

    color = (255, 255, 255)  # White color
    stroke = 1
    stroke_color = (0, 0, 0)  # Black color

    # Calculate the text position
    text_position = (20, height - 20)

    # Add text to frame
    cv2.putText(frame, current_time, text_position, font, font_scale, stroke_color, stroke*2, lineType=cv2.LINE_AA)
    cv2.putText(frame, current_time, text_position, font, font_scale, color, stroke, lineType=cv2.LINE_AA)


def getFilePath(relativePath):
    current_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(current_dir, relativePath)



def get_free_space(path='/'):
    """ Returns the free space in gigabytes. """
    total, used, free = shutil.disk_usage(path)

    return free / (2**30)  # Convert bytes to gigabytes
