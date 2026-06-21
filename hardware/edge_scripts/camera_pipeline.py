import cv2
import time

def run_camera_pipeline():
    # Initialize the webcam (0 is the default built-in laptop camera)
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("[ERROR] Could not open webcam.")
        return

    print("[SYSTEM] Camera pipeline initialized.")
    print("[SYSTEM] Pre-processing: Resizing to 416x416 and tracking FPS.")
    print("[SYSTEM] Press 'q' to quit the video window.")

    # Variables for FPS calculation
    prev_frame_time = 0
    new_frame_time = 0

    while True:
        # Capture frame-by-frame
        ret, frame = cap.read()
        if not ret:
            print("[ERROR] Failed to grab frame.")
            break

        # --- PRE-PROCESSING LAYER ---
        
        # 1. Resize to 416x416 (Strict requirement for YOLOv8-Nano)
        resized_frame = cv2.resize(frame, (416, 416)) 

        # 2. Color Conversion: OpenCV captures in BGR, but YOLO expects RGB
        # We process this conversion here so the AI team doesn't have to
        rgb_frame = cv2.cvtColor(resized_frame, cv2.COLOR_BGR2RGB) 

        # --- PERFORMANCE MONITORING ---
        
        # Calculate FPS to ensure we meet the >= 15 FPS requirement
        new_frame_time = time.time()
        fps = 1 / (new_frame_time - prev_frame_time)
        prev_frame_time = new_frame_time
        fps_text = f"FPS: {int(fps)}"

        # Draw the FPS counter on the screen in bright green
        cv2.putText(resized_frame, fps_text, (10, 30), 
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        # --- OUTPUT ---
        
        # Display the resulting frame 
        # (We display 'resized_frame' because OpenCV's imshow function expects BGR format)
        cv2.imshow('Simulated Jetson Edge Camera Pipeline', resized_frame)

        # Break the loop if 'q' is pressed on the keyboard
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Clean up and release the camera hardware
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    run_camera_pipeline()