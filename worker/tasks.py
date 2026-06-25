import base64
import numpy as np
import cv2
from worker.celery_app import app
from worker.vision_model import YOLOv7Analyzer

# Instantiate model globally so it's loaded only once per worker process memory space
analyzer = YOLOv7Analyzer()

@app.task(name="worker.tasks.process_frame")
def process_frame(base64_image_data: str):
    """
    Celery task to decode the base64 image and process it via YOLOv7.
    """
    try:
        # Decode base64 to bytes
        img_bytes = base64.b64decode(base64_image_data)
        
        # Convert bytes to numpy array for OpenCV
        np_arr = np.frombuffer(img_bytes, np.uint8)
        image = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
        
        if image is None:
            return {"error": "Failed to decode image data."}

        # Run Inference
        results = analyzer.analyze(image)
        
        return results

    except Exception as e:
        return {"error": str(e)}