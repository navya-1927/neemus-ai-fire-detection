# fire_classifier.py
import cv2
from ultralytics import YOLO

class FireClassifierEngine:
    def __init__(self, model_path="models/fire_classification/classifier.pt"):
        """
        Initializes the classification model.
        Make sure 'model_path' points to your trained classification weights.
        """
        print(f"[SYSTEM] Loading Fire Classification Model from {model_path}...")
        try:
            self.model = YOLO(model_path)
            print("[SYSTEM] Classification Model loaded successfully.")
        except Exception as e:
            print(f"[ERROR] Failed to load classification model: {e}")
            self.model = None

    def predict(self, image_crop):
        """
        Takes a cropped OpenCV image (numpy array), runs it through the classifier,
        and returns the predicted category name.
        """
        if self.model is None:
            return "Model Error"
            
        # YOLOv8 handles OpenCV (BGR) arrays directly. 
        # verbose=False prevents the console from being flooded with print statements every frame.
        results = self.model(image_crop, verbose=False)
        
        # Ensure we got a valid result back
        if len(results) == 0 or results[0].probs is None:
            return "Unknown"
            
        # Extract the highest probability class
        result = results[0]
        top1_index = result.probs.top1              # Index of the most likely class
        predicted_class = result.names[top1_index]  # Map index to the actual class name string (e.g., "Class_A_Fire")
        # confidence = float(result.probs.top1conf) # Optional: grab the confidence score if needed
        
        return predicted_class