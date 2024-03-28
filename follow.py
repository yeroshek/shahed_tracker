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

servoHorizontal = Servo(18, min_pulse_width=0.5/1000, max_pulse_width=2.5/1000)
servoVertical = Servo(15, min_pulse_width=0.5/1000, max_pulse_width=2.5/1000)

servoHorizontal.value = 0
servoVertical.value = VERTICAL_MIN

app = Flask(__name__)

orientation = 180 # 0, 90, 180, 270

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
    sensitivity_y = -0.00015
    
    vertical_adjustment = sensitivity_y * dy    
    new_vertical_value = servoVertical.value + vertical_adjustment
    new_vertical_value = max(min(new_vertical_value, VERTICAL_MAX), VERTICAL_MIN)
    
    servoVertical.value = new_vertical_value

    # print(dx, dy, servoVertical.value, vertical_adjustment, new_vertical_value)

    horizontal_adjustment = sensitivity_y * dx    
    new_horizontal_value = servoHorizontal.value + horizontal_adjustment
    new_horizontal_value = max(min(new_horizontal_value, VERTICAL_MAX), VERTICAL_MIN)

    servoHorizontal.value = new_horizontal_value

def generate_frames():
    cap = ht301_hacklib.HT301()
    prev_frame = None  # Initialize variable to store the previous frame

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                continue  # If no frame is captured, skip the rest of the loop

            frame = frame.astype(np.float32)

            frame_processed = rescale_intensity(
                equalize_hist(frame), in_range="image", out_range=(0, 255)
            ).astype(np.uint8)

            frame_processed = cv2.applyColorMap(frame_processed, cv2.COLORMAP_INFERNO)
            frame_processed = rotate_frame(frame_processed, orientation)

            # Convert to grayscale for motion detection
            gray = cv2.cvtColor(frame_processed, cv2.COLOR_BGR2GRAY)
            
            if prev_frame is not None:
                frame_diff = cv2.absdiff(prev_frame, gray)
                _, thresh = cv2.threshold(frame_diff, 25, 255, cv2.THRESH_BINARY)
                contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

                # Find the brightest area in the current frame for comparison
                boundary = detect_brightest_area_boundary(frame_processed)
                if boundary is not None:
                    x, y, w, h = boundary
                    for cnt in contours:
                        # Calculate bounding box of each contour
                        x_m, y_m, w_m, h_m = cv2.boundingRect(cnt)
                        # Check if the moving object's bounding box intersects with the brightest object's bounding box
                        if (x < x_m + w_m and x + w > x_m and y < y_m + h_m and y + h > y_m):
                            # If it intersects, it's our object of interest. Draw and track it.
                            frame_processed = draw_rectangle(frame_processed, x, y, w, h)
                            adjust_servo_position(x, y, w, h, frame_processed.shape)
                            break

            # Update the previous frame and proceed
            prev_frame = gray

            # Encoding and yielding the frame for web streaming
            _, buffer = cv2.imencode('.jpg', frame_processed)
            frame_bytes = buffer.tobytes()
            yield (b'--frame\r\n'b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

    except KeyboardInterrupt:
        servoHorizontal.value = 0
    except Exception as e:
        servoHorizontal.value = 0

    cap.release()


@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')


if __name__ == '__main__':
    app.run(debug=True, threaded=True, host='0.0.0.0')