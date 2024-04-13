import cv2
import time
import os
from datetime import datetime

def capture_video(frames, video_source=0, save_dir='./', video_length=15*60, fps=30, write_interval=2):
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # video codec

    def create_new_video_file(frame_size):
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')  # Get current time in the format YYYYMMDD_HHMMSS
        video_filename = os.path.join(save_dir, f'video_{timestamp}.mp4')
        return cv2.VideoWriter(video_filename, fourcc, fps, frame_size)

    while True:
        try:
            frame = frames[video_source]
        except KeyError:
            frame = None
            
        if frame is not None:
            break

    frame_size = (frame.shape[1], frame.shape[0])
    start_time = time.time()
    write_time = time.time()

    print(f'Frame size: {frame_size}')

    out = create_new_video_file(frame_size)

    while True:
        frame = frames[video_source]
        if frame is None:
            continue

        if time.time() - start_time >= video_length:
            out.release()
            start_time = time.time()
            out = create_new_video_file(frame_size)

        if time.time() - write_time >= write_interval:
            out.write(frame)
            write_time = time.time()
            print(f'Writing frame to video file: {write_time}')

    out.release()
    cv2.destroyAllWindows()