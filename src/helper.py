import cv2
import datetime

def addTimestamp(frame):
    # Get current time
    now = datetime.datetime.now()
    current_time = now.strftime("%Y-%m-%d %H:%M:%S")

    # Set font, scale, color, and thickness
    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 0.5
    color = (255, 255, 255)  # White color
    stroke = 1
    stroke_color = (0, 0, 0)  # Black color

    # Get frame dimensions
    height, width, _ = frame.shape

    # Calculate the text position
    text_position = (width - 200, height - 20)

    # Add text to frame
    cv2.putText(frame, current_time, text_position, font, font_scale, stroke_color, stroke*2, lineType=cv2.LINE_AA)
    cv2.putText(frame, current_time, text_position, font, font_scale, color, stroke, lineType=cv2.LINE_AA)
