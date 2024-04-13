import cv2
import time
import os
from datetime import datetime
import signal

SAVE_DIR = '../videos/'

def capture_video(frames, video_source=0, video_length=5, fps=30):
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = None

    def create_new_video_file(frame_size):
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        video_filename = os.path.join(SAVE_DIR, f'video_{timestamp}_{video_source}.mp4')
        return cv2.VideoWriter(video_filename, fourcc, fps, frame_size), video_filename

    # A precaution to release the video writer when the script is interrupted
    def signal_handler(sig, frame):
        nonlocal out
        if out is not None:
            out.release()
        cv2.destroyAllWindows()

    signals = [signal.SIGINT, signal.SIGTERM, signal.SIGHUP, signal.SIGQUIT, signal.SIGABRT]
    for sig in signals:
        signal.signal(sig, signal_handler)

    # Wait until the first frame is available
    while True:
        try:
            frame = frames[video_source]
        except KeyError:
            frame = None

        if frame is not None:
            break

    new_file_started = False
    frame_size = (frame.shape[1], frame.shape[0])

    print(f'Frame size: {frame_size}')

    out, video_filename = create_new_video_file(frame_size)

    try:
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

    except KeyboardInterrupt:
        print('Video capture stopped by user')
    finally:
        out.release()
        cv2.destroyAllWindows()
