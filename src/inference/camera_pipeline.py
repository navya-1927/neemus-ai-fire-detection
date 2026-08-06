# camera_pipeline.py
import cv2

class SensorCamera:
    def __init__(self, source=0):
        # Initializes the webcam when the class is called
        self.cap = cv2.VideoCapture(source)

        # Force OpenCV to keep only the absolute newest frame to prevent lag from phone cam
        self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

        if not self.cap.isOpened():
            print("[ERROR] Could not open webcam.")

    def get_frame(self):
        # Captures a single frame
        ret, frame = self.cap.read()
        if not ret:
            return False, None, None

        # --- PRE-PROCESSING LAYER ---
        # Resize to strict 416x416 for YOLOv8
        resized_frame = cv2.resize(frame, (416, 416)) 
        # Convert BGR to RGB
        preprocessed_frame = cv2.cvtColor(resized_frame, cv2.COLOR_BGR2RGB)

        # Returns the raw frame (for displaying) AND the pre-processed frame (for AI math)
        return True, resized_frame, preprocessed_frame

    def release(self):
        # Safely turns off the camera hardware
        self.cap.release()