import cv2
from flask import Flask, Response

# Define your Flask app
app = Flask(__name__)

def video_streaming(camera_id, frames):
    @app.route('/stream')
    def stream():
        def generate():
            while True:
                if camera_id in frames:
                    yield (b'--frame\r\n'
                           b'Content-Type: image/jpeg\r\n\r\n' + cv2.imencode('.jpg', frames[camera_id])[1].tobytes() + b'\r\n')
        
        return Response(generate(), mimetype='multipart/x-mixed-replace; boundary=frame')

    return app

# Start the process
if __name__ == "__main__":
    app = video_streaming(0)  # Stream video from the first camera
    app.run(host='0.0.0.0', port='5000')
