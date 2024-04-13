import cv2
from flask import Flask, Response, abort, redirect, url_for, send_from_directory
from helper import getFilePath, get_free_space
import os

# Define your Flask app
app = Flask(__name__)

MODES = ['HALT', 'SCAN']

video_directory = getFilePath('../videos')

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
        
        
        free_space_gb = get_free_space()
        links.append(f"<p><b>Free space: {free_space_gb:.2f} GB</b></p>")
        
        files = sorted(os.listdir(video_directory))

        for file in files:
            file_path = os.path.join(video_directory, file)
            download_link = url_for('download_file', filename=file)
            delete_link = url_for('delete_file', filename=file)
            style = 'width:50px; display:inline-block; text-align:center;'
            links.append(f"{file} - <a href='{download_link}'>Download</a><span style='{style}'>|</span><a href='{delete_link}'>Delete</a><br>")

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

    @app.route('/download/<filename>')
    def download_file(filename):
        return send_from_directory(directory=video_directory, path=filename, as_attachment=True)

    @app.route('/delete/<filename>')
    def delete_file(filename):
        file_path = os.path.join(video_directory, filename)
        if os.path.exists(file_path):
            os.remove(file_path)
        return redirect(url_for('index'))


    return app