import os
import cv2
import numpy as np
import onnxruntime as ort
import logging

logger = logging.getLogger(__name__)

class YOLOv7Analyzer:
    """
    Handles inference for YOLOv7 optimized via ONNX Runtime.
    """
    def __init__(self, model_path="/app/models/yolov7.onnx"):
        self.model_path = model_path
        self.input_shape = (640, 640)
        self.session = None
        self._load_model()

    def _load_model(self):
        if not os.path.exists(self.model_path):
            logger.warning(f"ONNX model not found at {self.model_path}. Running in MOCK mode.")
            return

        try:
            # For deployment, prioritize GPU if available, fallback to CPU
            providers = ['CUDAExecutionProvider', 'CPUExecutionProvider']
            self.session = ort.InferenceSession(self.model_path, providers=providers)
            self.input_name = self.session.get_inputs()[0].name
            logger.info("ONNX Runtime session initialized successfully.")
        except Exception as e:
            logger.error(f"Failed to load ONNX model: {e}")

    def preprocess(self, image: np.ndarray):
        """
        Resize, normalize, and format the image for YOLOv7 (HWC to CHW).
        """
        img = cv2.resize(image, self.input_shape)
        img = img[:, :, ::-1].transpose(2, 0, 1)  # BGR to RGB, to 3x640x640
        img = np.ascontiguousarray(img)
        img = img.astype(np.float32)
        img /= 255.0  # Normalize to [0, 1]
        if img.ndimension() == 3:
            img = np.expand_dims(img, axis=0) # Add batch dimension
        return img

    def analyze(self, image: np.ndarray):
        """
        Execute the ONNX graph and return metadata.
        """
        # --- Mock Mode (if model isn't mounted yet) ---
        if self.session is None:
            # Simulating detection metadata extraction
            return {
                "detections": [
                    {"class_id": 0, "label": "person", "confidence": 0.95, "bbox": [100, 150, 200, 350]},
                    {"class_id": 2, "label": "car", "confidence": 0.88, "bbox": [400, 200, 500, 300]}
                ],
                "metadata": {
                    "image_size": f"{image.shape[1]}x{image.shape[0]}",
                    "mode": "mock_inference"
                }
            }

        # --- Actual Inference Mode ---
        try:
            input_tensor = self.preprocess(image)
            outputs = self.session.run(None, {self.input_name: input_tensor})
            
            # Note: YOLOv7 ONNX output parsing varies heavily depending on the export script used
            # This is a generalized placeholder parsing structure for standard bounding boxes
            detections = []
            
            # Assuming output[0] shape is [batch, num_boxes, attributes] (x, y, w, h, conf, class...)
            raw_boxes = outputs[0][0]
            
            for box in raw_boxes:
                # Mock threshold implementation
                if box[4] > 0.5:  
                    detections.append({
                        "class_id": int(np.argmax(box[5:])),
                        "confidence": float(box[4]),
                        "bbox": [float(x) for x in box[0:4]] # x_center, y_center, w, h
                    })

            return {
                "detections": detections,
                "metadata": {
                    "image_size": f"{image.shape[1]}x{image.shape[0]}",
                    "mode": "onnx_inference"
                }
            }
        except Exception as e:
            logger.error(f"Inference error: {e}")
            return {"error": str(e)}