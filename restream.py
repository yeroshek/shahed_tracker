from flask import Flask, Response
import cv2
import os
from pathlib import Path

app = Flask(__name__)

# Directory where video files are stored
VIDEO_DIR = '../Videos'

def generate_frames():
    video_path = find_latest_video(VIDEO_DIR)
    print(video_path)

    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

    # total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    # cap.set(cv2.CAP_PROP_POS_FRAMES, total_frames - 1)
    
    # print(total_frames)
    
    

    while True:
        # Try to set the position to the last known frame count
        success, frame = cap.read()

        # if not success:
        #     # Try moving the read position slightly back in case we're at the very end
        #     total_frames = max(total_frames - 10, 0)  # Adjust this value as needed
        #     continue


        # Convert the frame format from BGR to JPEG
        _, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()

        yield (b'--frame\r\n'b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')



if __name__ == '__main__':
    app.run(debug=True, threaded=True, host='0.0.0.0')
