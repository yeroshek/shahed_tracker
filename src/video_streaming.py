import cv2
from flask import Flask, Response, abort

# Define your Flask app
app = Flask(__name__)

def video_streaming(frames):
    @app.route('/')
    def index():
        links = [f"<a href='/stream/{id}'>Camera {id}</a>" for id in frames.keys()]
        return "<br>".join(links)

    @app.route('/stream/<int:camera_id>')
    def stream(camera_id):
        if camera_id not in frames:
            abort(404)  # Return a 404 error if camera_id is not in frames

        def generate():
            while True:
                yield (b'--frame\r\n'
                    b'Content-Type: image/jpeg\r\n\r\n' + cv2.imencode('.jpg', frames[camera_id])[1].tobytes() + b'\r\n')

        return Response(generate(), mimetype='multipart/x-mixed-replace; boundary=frame')

    return app