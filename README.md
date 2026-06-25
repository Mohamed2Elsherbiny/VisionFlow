VisionFlow: Event-Driven Real-Time Video Analytics Pipeline

This repository contains the microservice stack for VisionFlow, leveraging FastAPI, Celery, Redis, and ONNX Runtime (YOLOv7).

Project Architecture

API (Port 8000): Ingests video frames.
Redis (Port 6379): Acts as the message broker for the event-driven architecture.
Worker: Asynchronous agent running YOLOv7 inferences securely disconnected from the main web thread.

How to Deploy

Prepare Model Folder:Create a models directory in the root of the project and place your optimized yolov7.onnx model inside.

mkdir models
# Move your yolov7.onnx file into ./models/
(Note: If the ONNX file isn't found, the worker gracefully falls back to a "Mock Inference" mode to ensure pipelines can be tested immediately).

Start the Microservices Stack:

docker-compose up --build -d

Monitor Worker Logs (To watch the CV pipeline process tasks in real-time):

docker logs -f visionflow-worker

API Usage Example1.

Submit a frame for processing:

curl -X POST "http://localhost:8000/analyze-frame/" \
     -H "accept: application/json" \
     -H "Content-Type: multipart/form-data" \
     -F "file=@/path/to/test_image.jpg"

Response:{
  "message": "Frame queued successfully",
  "task_id": "8f8b8e3a-4423-45ab-a279-...",
  "status_endpoint": "/tasks/8f8b8e3a-..."
}

2. Check processing results:

curl -X GET "http://localhost:8000/tasks/8f8b8e3a-..."

Response (Once Celery finishes the async task):{
  "task_id": "8f8b8e3a-...",
  "status": "Completed",
  "results": {
    "detections": [...],
    "metadata": { "image_size": "1920x1080", "mode": "onnx_inference" }
  }
}
