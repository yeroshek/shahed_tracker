import frame_manager
import video_streaming
import video_capture
import multiprocessing

if __name__ == "__main__":
    with multiprocessing.Manager() as manager:
        frames = manager.dict()

        # Start frame manager process
        frame_manager_process = multiprocessing.Process(target=frame_manager.capture_frames, args=(0, frames))
        frame_manager_process.start()

        # Start video capture process
        video_capture_process = multiprocessing.Process(target=video_capture.capture_video, args=(frames,))
        video_capture_process.start()

        # Start video streaming process
        app = video_streaming.video_streaming(0, frames)
        video_streaming_process = multiprocessing.Process(target=app.run, kwargs={'host': '0.0.0.0', 'port': '5000'})
        video_streaming_process.start()

        # Join the processes
        frame_manager_process.join()
        video_capture_process.join()
        video_streaming_process.join()