#!/usr/bin/python3
import numpy as np
import cv2
import math
import ht301_hacklib
import utils
import time
from skimage.exposure import rescale_intensity, equalize_hist
from flask import Flask, Response

app = Flask(__name__)

draw_temp = True
orientation = 0  # 0, 90, 180, 270


def increase_luminance_contrast(frame):
    lab = cv2.cvtColor(frame, cv2.COLOR_BGR2LAB)
    l_channel, a, b = cv2.split(lab)

    # Applying CLAHE to L-channel
    # feel free to try different values for the limit and grid size:
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    cl = clahe.apply(l_channel)

    # merge the CLAHE enhanced L-channel with the a and b channel
    limg = cv2.merge((cl, a, b))
    frame = enhanced_img = cv2.cvtColor(limg, cv2.COLOR_LAB2BGR)
    return frame


def rotatate_coordinate(pos, shape, orientation):
    x, y = pos
    len_x, len_y = shape
    if orientation == 0:
        return x, y
    elif orientation == 90:
        return y, len_x - x
    elif orientation == 180:
        return len_x - x, len_y - y
    elif orientation == 270:
        return len_y - y, x


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


def draw_rectangle_around_brightest(frame):
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

        # Draw the rectangle
        cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)

    return frame


class FpsCounter:
    def __init__(self, alpha=0.9, init_frame_count=10):
        self.alpha = alpha
        self.init_frame_count = init_frame_count
        self.frame_times = []
        self.start_time = time.time()
        self.ema_duration = None

    def update(self):
        current_time = time.time()
        frame_duration = current_time - self.start_time

        if len(self.frame_times) < self.init_frame_count:
            self.frame_times.append(frame_duration)
            self.ema_duration = sum(self.frame_times) / len(self.frame_times)
        else:
            self.ema_duration = (
                self.alpha * self.ema_duration + (1.0 - self.alpha) * frame_duration
            )

        self.start_time = current_time

    def get_fps(self):
        if self.ema_duration is not None:
            return 1.0 / self.ema_duration
        else:
            return None


def generate_frames():

    cap = ht301_hacklib.HT301()
    window_name = str(type(cap).__name__)
    # cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)

    fps_counter = FpsCounter(alpha=0.8)
    upscale_factor = 2

    while True:
        ret, frame = cap.read()
        fps_counter.update()
        shape = frame.shape[0]
        info, lut = cap.info()
        frame = frame.astype(np.float32)

        # Sketchy auto-exposure
        frame = rescale_intensity(
            equalize_hist(frame), in_range="image", out_range=(0, 255)
        ).astype(np.uint8)

        # frame = cv2.applyColorMap(frame, cv2.COLORMAP_INFERNO)

        # frame = increase_luminance_contrast(frame)

        frame = rotate_frame(frame, orientation)

        # frame = draw_rectangle_around_brightest(frame)

        # frame = np.kron(frame, np.ones((upscale_factor, upscale_factor, 1))).astype(
        #     np.uint8
        # )
        if draw_temp:
            utils.drawTemperature(
                frame,
                rotatate_coordinate(
                    map(lambda x: upscale_factor * x, info["Tmin_point"]),
                    (cap.FRAME_WIDTH * upscale_factor, cap.FRAME_HEIGHT * upscale_factor),
                    orientation,
                ),
                info["Tmin_C"],
                (255, 128, 128),
            )
            utils.drawTemperature(
                frame,
                rotatate_coordinate(
                    map(lambda x: upscale_factor * x, info["Tmax_point"]),
                    (cap.FRAME_WIDTH * upscale_factor, cap.FRAME_HEIGHT * upscale_factor),
                    orientation,
                ),
                info["Tmax_C"],
                (0, 128, 255),
            )
            utils.drawTemperature(
                frame,
                rotatate_coordinate(
                    map(lambda x: upscale_factor * x, info["Tcenter_point"]),
                    (cap.FRAME_WIDTH * upscale_factor, cap.FRAME_HEIGHT * upscale_factor),
                    orientation,
                ),
                info["Tcenter_C"],
                (255, 255, 255),
            )
            # draw fps

            # to keep the fps displayed from jittering too much, we average the last 10 frames
            cv2.putText(
                frame,
                f"FPS: {fps_counter.get_fps():0.1f}",
                (2, 12),
                cv2.FONT_HERSHEY_PLAIN,
                1,
                (255, 255, 255),
                1,
                cv2.LINE_8,
            )

        # cv2.imshow(window_name, frame)

        # Web
        _, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()

        yield (b'--frame\r\n'b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')



        # key = cv2.waitKey(1) & 0xFF
        # if key == ord("q"):
        #     break
        # if key == ord("u"):
        #     cap.calibrate()
        # if key == ord("k"):
        #     cap.temperature_range_normal()
        #     # some delay is needed before calibration
        #     for _ in range(50):
        #         cap.read()
        #     cap.calibrate()
        # if key == ord("l"):
        #     cap.temperature_range_high()
        #     # some delay is needed before calibration
        #     for _ in range(50):
        #         cap.read()
        #     cap.calibrate()
        # if key == ord("s"):
        #     cv2.imwrite(time.strftime("%Y-%m-%d_%H-%M-%S") + ".png", frame)
        # if key == ord("o"):
        #     orientation = (orientation - 90) % 360
        #     (_, _, w, h) = cv2.getWindowImageRect(window_name)
        #     cv2.resizeWindow(window_name, h, w)

    cap.release()
    # cv2.destroyAllWindows()


@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')


if __name__ == '__main__':
    app.run(debug=True, threaded=True, host='0.0.0.0')
