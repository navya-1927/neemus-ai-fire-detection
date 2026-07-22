# fire_detector.py
from ultralytics import YOLO

class YoloInferenceEngine:
    def __init__(self, model_path="best.pt"):
        print(f"[AI] Loading YOLOv8 Model from {model_path}...")
        self.model = YOLO(model_path, task="detect") 
        self.confidence_threshold = 0.2

    def analyze_frame(self, rgb_frame):
        # Run the AI math on the pre-processed frame
        results = self.model.predict(source=rgb_frame, imgsz=416, conf=self.confidence_threshold, verbose=True)
        
        detections = []
        
        # Extract the bounding box coordinates and confidence scores
        for result in results:
            for box in result.boxes:
                confidence = float(box.conf[0])
                class_id = int(box.cls[0])
                
                # Assumes class 0 is Flame and class 1 is Smoke
                label = "Flame" if class_id == 0 else "Smoke"
                
                # Get coordinates for the bounding box
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                
                # Package it up cleanly to send back to main.py
                detections.append({
                    'class': label,
                    'confidence': confidence,
                    'p1': (x1, y1),
                    'p2': (x2, y2)
                })
                
        return detections
    
    