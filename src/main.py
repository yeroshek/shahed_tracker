import multiprocessing

import frame_manager
import video_streaming
import video_capture
import mode_scan

if __name__ == "__main__":
    with multiprocessing.Manager() as manager:
        frames = manager.dict()
        mode = manager.Value('s', 'SCAN')

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
        app = video_streaming.video_streaming(frames, mode)
        video_streaming_process = multiprocessing.Process(target=app.run, kwargs={'host': '0.0.0.0', 'port': '5000'})
        video_streaming_process.start()

        # Start mode scan process
        mode_scan_process = multiprocessing.Process(target=mode_scan.start_scan, args=(mode,))
        mode_scan_process.start()

        # Join the processes
        for process in frame_manager_processes:
            process.join()
        for process in video_capture_processes:
            process.join()
        video_streaming_process.join()
        mode_scan_process.join()
