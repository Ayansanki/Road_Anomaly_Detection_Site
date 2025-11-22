import os
os.environ['TORCH_DEVICE_BACKEND_AUTOLOAD'] = '0'

import cv2
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from ultralytics import YOLO
from pathlib import Path

from road_anomaly_detection import settings



model = YOLO('road_anomaly_detection_model/models/best.pt')  # load a custom model


def draw_boxes_on_image(image_path, predictions, output_path, class_names):
    """
    Draw bounding boxes on image with detection results
    
    Args:
        image_path: Path to input image
        predictions: YOLO predictions
        output_path: Path to save annotated image
        class_names: Dictionary of class IDs to class names
    """
    # Read image
    image = cv2.imread(image_path)
    if image is None:
        print(f"Error reading image: {image_path}")
        return None
    
    img_height, img_width = image.shape[:2]
    
    # Colors for each class (BGR format for OpenCV)
    colors = {
        0: (0, 255, 0),      # D00 - Green
        1: (255, 0, 0),      # D10 - Blue
        2: (0, 165, 255),    # D20 - Orange
        3: (255, 0, 255)     # D40 - Magenta
    }
    
    # Process predictions
    for result in predictions:
        if len(result.boxes) > 0:
            for box in result.boxes:
                # Get bounding box coordinates
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                
                # Get class and confidence
                class_id = int(box.cls[0])
                confidence = float(box.conf[0])
                class_name = class_names.get(class_id, f"Class_{class_id}")
                
                # Get color for this class
                color = colors.get(class_id, (255, 255, 255))
                
                # Draw rectangle
                cv2.rectangle(image, (x1, y1), (x2, y2), color, 2)
                
                # Prepare label text
                label = f"{class_name} ({confidence:.2f})"
                
                # Draw label background
                label_size = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)[0]
                label_y = max(20, y1 - 10)
                cv2.rectangle(image, (x1, label_y - label_size[1] - 5), 
                            (x1 + label_size[0], label_y + 5), color, -1)
                
                # Draw label text
                cv2.putText(image, label, (x1, label_y), 
                          cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
    
    # Save annotated image
    cv2.imwrite(output_path, image)
    print(f"✓ Annotated image saved: {output_path}")
    
    return image




def detect_and_annotate_image(image_path, model, class_names, output_dir):
    """
    Detect damages in image, draw boxes, and save results
    """

    json_structure = {
        "image_name": Path(image_path).name,
        "detections": []
    }

    print(f"\n{'='*70}")
    print(f"Processing: {Path(image_path).name}")
    print(f"{'='*70}")
    
    # Run inference
    results = model(image_path, conf=0.3, verbose=False)
    
    # Print detection info
    if len(results) > 0 and len(results[0].boxes) > 0:
        print(f"\n✓ Detections found: {len(results[0].boxes)}")
        
        for idx, box in enumerate(results[0].boxes):
            class_id = int(box.cls[0])
            confidence = float(box.conf[0])
            x1, y1, x2, y2 = map(float, box.xyxy[0])
            area = (x2 - x1) * (y2 - y1)
            
            class_name = class_names.get(class_id, f"Class_{class_id}")

            json_structure["detections"].append({
                "class": class_name,
                "confidence": round(confidence, 4),
                "bounding_box": {
                    "x1": int(x1),
                    "y1": int(y1),
                    "x2": int(x2),
                    "y2": int(y2)
                },
                "area_pixels": int(area)
            })

        best = max(json_structure["detections"], key=lambda x: x['confidence'])            
        json_structure['main_class'] = best['class']
        json_structure['main_confidence'] = best['confidence']

    else:
        json_structure["detections"] = None
        print("✗ No detections found")
    
    # Draw boxes on image
    # annotated_path = os.path.join(output_dir, f"annotated_{Path(image_path).stem}.jpg")
    draw_boxes_on_image(image_path, results, image_path, class_names)
        
    return json_structure

def classifier(input_image_path, model = model, ):
    if not os.path.exists(input_image_path):
        return None
    
    class_names = {
        0: 'D00_Longitudinal_Crack',
        1: 'D10_Transverse_Crack',
        2: 'D20_Alligator_Crack',
        3: 'D40_Pothole'
    }

    return detect_and_annotate_image(input_image_path, model, class_names, input_image_path)





if __name__ == "__main__":
    
    class_names = {
        0: 'D00_Longitudinal_Crack',
        1: 'D10_Transverse_Crack',
        2: 'D20_Alligator_Crack',
        3: 'D40_Pothole'
    }
    
    # Input image path
    input_image_path = 'data/1.jpg'  # Replace with your image path
    
    # Output directory
    output_directory = 'output'
    os.makedirs(output_directory, exist_ok=True)
    
    # Run detection and annotation
    print(detect_and_annotate_image(input_image_path, model, class_names, output_directory))