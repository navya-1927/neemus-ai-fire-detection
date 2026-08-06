# main.py
import cv2
import time
import threading
import queue
from collections import deque
from camera_pipeline import SensorCamera
from fire_detector import YoloInferenceEngine
from fire_classifier import FireClassifierEngine
import hardware_controller

camera_url = "https://10.11.158.246:8080/video"
video1 = "sample_data/fire_video.mp4"
video2 = "sample_data/fire_vid2.mp4"
video3 = "sample_data/fire_vid3.mp4"
video4 = "sample_data/fire_vid4.mp4"
e_fire = "sample_data/e_fire.mp4"
oil_fire = "sample_data/oil_fire.mp4"
confidence = 0.2

def main():
    # 1. Initialize all modules
    print("[SYSTEM] Starting Real-Time Workflow Orchestration...")

    camera = SensorCamera(source=video2)#0 for laptop cam, url for phone cam

    detector = YoloInferenceEngine()
    classifier = FireClassifierEngine()
    hardware_controller.initialize_hardware()

    # Create a tracker to hold frame timestamps for the moving average
    # maxlen=300 assumes a maximum of 60 FPS * 5 seconds
    frame_times = deque(maxlen=300)


    # --- VIDEO EXPORT SETUP ---
    # 1. Define the codec (MP4V is standard for .mp4 files on Linux)
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')

    # 2. Get the exact width and height from your camera/video source
    # (We read one dummy frame just to get the dimensions)
    dummy_ret, dummy_frame, dummy_pre = camera.get_frame()
    if dummy_ret:
        height, width = dummy_frame.shape[:2]
    else:
        # Fallback if the camera didn't open instantly
        width, height = 640, 480 

    # 3. Create the writer object
    # Parameters: filename, codec, FPS (e.g., 15.0), and (width, height)
    #out_video = cv2.VideoWriter('demo_output.mp4', fourcc, 30.0, (width, height))

    out_video = ThreadedVideoWriter('sample_data/demo_output.mp4', fourcc, 15.0, (width, height))
    # --------------------------



    # 2. Core Real-Time Processing Loop
    while True:
        # Input Layer: Get raw and pre-processed frames
        ret, raw_frame, preprocessed_frame = camera.get_frame()
        if not ret:
            print("[ERROR] Camera stream interrupted.")
            break

        # Processing Layer: Run inference on the pre-processed matrix
        detections = detector.analyze_frame(preprocessed_frame)

        # Decision Layer: Evaluate confidence and classification thresholds
        fire_triggered = False
        for det in detections:
            if det['class'] in ['Flame', 'Smoke'] and det['confidence'] > confidence:
                fire_triggered = True
                # Draw bounding box on the raw frame for display
                cv2.rectangle(raw_frame, det['p1'], det['p2'], (0, 0, 255), 2)

        # Output Layer: Coordinate response based on decision logic
        # Get the height (h) and width (w) of the current camera frame
        h, w = raw_frame.shape[:2]
        if fire_triggered:
            hardware_controller.trigger_alarms()
            fire_category = classifier.predict(preprocessed_frame)
            #alert_text = f"!!! FIRE DETECTED:\n {fire_category}"
            #cv2.putText(raw_frame, alert_text, (30, h-25 ),cv2.FONT_HERSHEY_TRIPLEX, 0.6, (0, 0, 255), 2)
            cv2.putText(raw_frame, "!!! FIRE DETECTED !!!", (30, h-10 ),cv2.FONT_HERSHEY_TRIPLEX, 0.8, (0, 0, 255), 2)

        else:
            cv2.putText(raw_frame, "SYSTEM NORMAL", (30, h-10 ), cv2.FONT_HERSHEY_TRIPLEX, 0.8, (0, 255, 0), 2)
            hardware_controller.reset_alarms()

        # Performance Monitoring
        # 1. READ FRAME
        if raw_frame is None:
            break

        # --- NEW 5-SECOND FPS CALCULATOR ---
        current_time = time.time()
        frame_times.append(current_time)

        # Delete any timestamps that are older than 5 seconds
        while frame_times and frame_times[0] < current_time - 5.0:
            frame_times.popleft()

        # Calculate average: (Total frames in queue) / (Time between oldest and newest frame)
        elapsed_time = current_time - frame_times[0]
        avg_fps = len(frame_times) / elapsed_time if elapsed_time > 0 else 0.0
        cv2.putText(raw_frame, f"Avg FPS: {avg_fps:.0f}", (10, 18), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255,0,0), 2)
        
        
        # Display Output
        window_name = "Embedded AI Fire Detection"
    
        # Tell OpenCV to allow this window to be resized by the OS
        cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
        
        # Force the window to open at a much larger size (Width, Height)
        cv2.resizeWindow(window_name, 800, 800)

        #  Save the fully drawn frame to the video file
        out_video.write(raw_frame)
        cv2.imshow(window_name, raw_frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            print("[SYSTEM] Stream closed by user.")
            break

    camera.release()
    cv2.destroyAllWindows()


class ThreadedVideoWriter:
    def __init__(self, filename, fourcc, fps, frame_size):
        self.writer = cv2.VideoWriter(filename, fourcc, fps, frame_size)
        # Create a bucket (queue) that can hold up to 128 frames in RAM
        self.queue = queue.Queue(maxsize=128) 
        
        # Start the background worker
        self.thread = threading.Thread(target=self._write_frames, daemon=True)
        self.thread.start()

    def _write_frames(self):
        # This loop runs completely invisibly in the background
        while True:
            frame = self.queue.get()
            if frame is None: # The signal to stop
                break
            self.writer.write(frame)

    def write(self, frame):
        # Toss the frame in the bucket and instantly return to the main loop!
        if not self.queue.full():
            self.queue.put(frame.copy()) # Copy prevents memory corruption

    def release(self):
        # Tell the worker to pack up and go home
        self.queue.put(None)
        self.thread.join()
        self.writer.release()

if __name__ == "__main__":
    main()