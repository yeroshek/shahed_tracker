import multiprocessing
import cv2

import frame_manager
import video_streaming
import video_capture

if __name__ == "__main__":
    with multiprocessing.Manager() as manager:
        frames = manager.dict()
        mode = manager.Value('s', 'HALT')

        # Camera indexes
        camera_indexes = [0, 2]

        # Start frame manager and video capture processes for each camera
        frame_manager_processes = []
        video_capture_processes = []
        for index in camera_indexes:
            frame_manager_process = multiprocessing.Process(target=frame_manager.capture_frames, args=(frames, index))
            frame_manager_process.start()
            frame_manager_processes.append(frame_manager_process)

            video_capture_process = multiprocessing.Process(target=video_capture.capture_video, args=(frames, index))
            video_capture_process.start()
            video_capture_processes.append(video_capture_process)

        # Start video streaming process
        app = video_streaming.video_streaming(frames)
        video_streaming_process = multiprocessing.Process(target=app.run, kwargs={'host': '0.0.0.0', 'port': '5000'})
        video_streaming_process.start()

        # Join the processes
        for process in frame_manager_processes:
            process.join()
        for process in video_capture_processes:
            process.join()
        video_streaming_process.join()