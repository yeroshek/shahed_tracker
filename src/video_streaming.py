import cv2
from flask import Flask, Response, abort, redirect, url_for

# Define your Flask app
app = Flask(__name__)

MODES = ['HALT', 'SCAN']

def video_streaming(frames, mode):
    # @app.route('/switch_mode/<new_mode>')
    # def switch_mode(new_mode):
    #     nonlocal mode
    #     if new_mode.upper() in MODES:
    #         mode.value = new_mode.upper()
    #     return redirect(url_for('index'))

    @app.route('/')
    def index():
        mode_display = "<p>Mode: "
        mode_display += ' | '.join([f"<b>{m}</b>" if m == mode.value else f"{m}" for m in MODES])
        mode_display += "</p>"

        links = [f"<a href='/stream/{id}'>Camera {id}</a>" for id in frames.keys()]
        links.append(mode_display)
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