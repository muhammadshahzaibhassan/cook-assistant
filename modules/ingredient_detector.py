import torch
import cv2
from PIL import Image
import numpy as np

class IngredientDetector:
    def __init__(self):
        # Use YOLOv5 for object detection (pre-trained on COCO)
        self.model = self._load_model()
        self.ingredient_classes = self._get_food_classes()
        
    def _load_model(self):
        """Load YOLOv5 model"""
        try:
            # YOLOv5 small model (fastest)
            model = torch.hub.load('ultralytics/yolov5', 'yolov5s', pretrained=True)
            return model
        except:
            # Fallback to OpenCV DNN if YOLO fails
            return None
    
    def _get_food_classes(self):
        """Map COCO classes to food ingredients"""
        # YOLOv5 COCO classes that are food-related
        food_mapping = {
            'apple': 'apple',
            'banana': 'banana',
            'orange': 'orange',
            'broccoli': 'broccoli',
            'carrot': 'carrot',
            'hot dog': 'sausage',
            'pizza': 'pizza',
            'donut': 'donut',
            'cake': 'cake',
            'sandwich': 'sandwich',
            'bowl': 'bowl',  # often contains food
            'bottle': 'bottle',
            'wine glass': 'wine',
            'cup': 'cup'
        }
        return food_mapping
    
    def detect_from_image(self, image_path):
        """Detect ingredients from image"""
        if self.model is None:
            return self._detect_fallback(image_path)
        
        # Run inference
        results = self.model(image_path)
        
        # Parse results
        detections = []
        if results.xyxy[0].shape[0] > 0:
            for *box, conf, cls in results.xyxy[0]:
                class_name = results.names[int(cls)]
                if class_name in self.ingredient_classes:
                    ingredient = self.ingredient_classes[class_name]
                    detections.append({
                        'ingredient': ingredient,
                        'confidence': float(conf),
                        'bbox': [float(b) for b in box]
                    })
        
        return detections
    
    def _detect_fallback(self, image_path):
        """Simple color-based detection as fallback"""
        # This is a simplified version - you can expand this
        image = cv2.imread(image_path)
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        
        # Simple color ranges for common foods
        detections = []
        
        # Red items (tomatoes, apples)
        lower_red = np.array([0, 100, 100])
        upper_red = np.array([10, 255, 255])
        mask = cv2.inRange(hsv, lower_red, upper_red)
        if cv2.countNonZero(mask) > 100:
            detections.append({'ingredient': 'tomato', 'confidence': 0.5})
        
        # Green items (vegetables)
        lower_green = np.array([35, 100, 100])
        upper_green = np.array([85, 255, 255])
        mask = cv2.inRange(hsv, lower_green, upper_green)
        if cv2.countNonZero(mask) > 100:
            detections.append({'ingredient': 'vegetable', 'confidence': 0.5})
        
        return detections
    
    def draw_detections(self, image_path, detections):
        """Draw bounding boxes on image"""
        img = cv2.imread(image_path)
        for det in detections:
            x1, y1, x2, y2 = map(int, det['bbox'][:4])
            cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
            label = f"{det['ingredient']} ({det['confidence']:.2f})"
            cv2.putText(img, label, (x1, y1-10), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        return img