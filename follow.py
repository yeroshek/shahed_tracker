#!/usr/bin/python3
import numpy as np
import cv2
import math
import ht301_hacklib
import utils
import time
from skimage.exposure import rescale_intensity, equalize_hist
from flask import Flask, Response
from gpiozero import Device, PWMOutputDevice, DigitalInputDevice, Servo
from gpiozero.pins.pigpio import PiGPIOFactory

VERTICAL_MIN = -0.85
VERTICAL_MAX = 0.85

Device.pin_factory = PiGPIOFactory()

servoHorizontal = Servo(14, min_pulse_width=0.5/1000, max_pulse_width=2.5/1000)
servoVertical = Servo(15, min_pulse_width=0.5/1000, max_pulse_width=2.5/1000)

servoHorizontal.value = 0
servoVertical.value = VERTICAL_MIN

app = Flask(__name__)

orientation = 0 # 0, 90, 180, 270

def rotate_frame(frame, orientation):
    if orientation == 0:
        return frame
    elif orientation == 90:
        return np.rot90(frame).copy()
    elif orientation == 180:
        return np.rot90(frame, 2).copy()
    elif orientation == 270:
        return np.rot90(frame, 3).copy()
    else:
        return frame

def detect_brightest_area_boundary(frame):
    # Convert the image to grayscale
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Apply thresholding to isolate the brightest areas
    _, thresholded = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY)

    # Find contours in the thresholded image
    contours, _ = cv2.findContours(thresholded, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # If any contours were found
    if contours:
        # Find the largest contour
        largest_contour = max(contours, key=cv2.contourArea)

        # Get the rectangle that contains the contour
        x, y, w, h = cv2.boundingRect(largest_contour)

        return x, y, w, h

    return None

def draw_rectangle(frame, x, y, w, h):
    # Draw the rectangle
    cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)

    return frame

def adjust_servo_position(x, y, w, h, frame_shape):
    # Calculate the center of the frame
    frame_center_x, frame_center_y = frame_shape[1] // 2, frame_shape[0] // 2
    
    # Calculate the center of the bright area
    bright_center_x, bright_center_y = x + w // 2, y + h // 2
    
    # Calculate the difference between the centers
    dx = bright_center_x - frame_center_x
    dy = bright_center_y - frame_center_y
    
    # Adjust the servo positions based on the difference
    # The sensitivity factors (0.001) determine how much the servo moves per pixel difference
    # You might need to adjust these factors based on your setup
    # sensitivity_x = 0.001
    sensitivity_y = -0.0001
    
    # horizontal_adjustment = sensitivity_x * dx
    vertical_adjustment = sensitivity_y * dy
    
    # Update servo positions
    # Make sure the adjustments are within the servo's range
    # new_horizontal_value = servoHorizontal.value + horizontal_adjustment
    new_vertical_value = servoVertical.value + vertical_adjustment
    
    # Clamp the servo values to their allowed range to avoid errors
    # new_horizontal_value = max(min(new_horizontal_value, 1), -1)
    new_vertical_value = max(min(new_vertical_value, VERTICAL_MAX), VERTICAL_MIN)
    
    # servoHorizontal.value = new_horizontal_value
    servoVertical.value = new_vertical_value

    print(dy, servoVertical.value, vertical_adjustment, new_vertical_value)

def generate_frames():

    cap = ht301_hacklib.HT301()

    while True:
        ret, frame = cap.read()
        frame = frame.astype(np.float32)

        # Sketchy auto-exposure
        frame = rescale_intensity(
            equalize_hist(frame), in_range="image", out_range=(0, 255)
        ).astype(np.uint8)

        frame = cv2.applyColorMap(frame, cv2.COLORMAP_INFERNO)

        frame = rotate_frame(frame, orientation)

        boundary = detect_brightest_area_boundary(frame)

        if boundary is not None:
            x, y, w, h = boundary
            frame = draw_rectangle(frame, x, y, w, h)

            adjust_servo_position(x, y, w, h, frame.shape)
            
        # Web
        _, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()

        yield (b'--frame\r\n'b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

    cap.release()


@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')


if __name__ == '__main__':
    app.run(debug=True, threaded=True, host='0.0.0.0')