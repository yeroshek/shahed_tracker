import cv2
import time
import os
from datetime import datetime

SAVE_DIR = '../videos/'

def capture_video(frames, video_source=0, video_length=5, fps=30):
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # video codec
    new_file_started = False

    def create_new_video_file(frame_size):
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')  # Get current time in the format YYYYMMDD_HHMMSS
        video_filename = os.path.join(SAVE_DIR, f'video_{timestamp}.mp4')
        return cv2.VideoWriter(video_filename, fourcc, fps, frame_size), video_filename

    while True:
        try:
            frame = frames[video_source]
        except KeyError:
            frame = None
            
        if frame is not None:
            break

    frame_size = (frame.shape[1], frame.shape[0])
    start_time = time.time()

    print(f'Frame size: {frame_size}')

    out, video_filename = create_new_video_file(frame_size)

    while True:
        frame = frames[video_source]
        if frame is None:
            continue

        out.write(frame)

        current_time = datetime.now()
        if current_time.minute % video_length == 0 and current_time.second == 0:
            if not new_file_started:
                out.release()
                out, video_filename = create_new_video_file(frame_size)
                new_file_started = True
        else:
            new_file_started = False

    out.release()
    cv2.destroyAllWindows()