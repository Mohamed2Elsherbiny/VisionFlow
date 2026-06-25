from fastapi import FastAPI, UploadFile, File, HTTPException
from celery import Celery
from celery.result import AsyncResult
import base64
import os

app = FastAPI(
    title="VisionFlow API",
    description="Event-Driven Real-Time Video Analytics Pipeline",
    version="1.0.0"
)

# Initialize Celery client to connect to the broker
CELERY_BROKER_URL = os.environ.get("CELERY_BROKER_URL", "redis://localhost:6379/0")
CELERY_RESULT_BACKEND = os.environ.get("CELERY_RESULT_BACKEND", "redis://localhost:6379/1")

celery_app = Celery(
    "visionflow_tasks",
    broker=CELERY_BROKER_URL,
    backend=CELERY_RESULT_BACKEND
)

@app.get("/")
def health_check():
    return {"status": "healthy", "service": "VisionFlow API"}

@app.post("/analyze-frame/")
async def analyze_frame(file: UploadFile = File(...)):
    """
    Ingest a video frame (image) for asynchronous YOLOv7 processing.
    """
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File provided is not an image.")
    
    # Read image bytes and encode to base64 for safe JSON serialization over Redis
    contents = await file.read()
    encoded_image = base64.b64encode(contents).decode('utf-8')
    
    # Dispatch task to Celery Worker
    task = celery_app.send_task("worker.tasks.process_frame", args=[encoded_image])
    
    return {
        "message": "Frame queued successfully",
        "task_id": task.id,
        "status_endpoint": f"/tasks/{task.id}"
    }

@app.get("/tasks/{task_id}")
def get_task_status(task_id: str):
    """
    Retrieve the status and results of a submitted frame analysis.
    """
    task_result = AsyncResult(task_id, app=celery_app)
    
    if task_result.state == 'PENDING':
        return {"task_id": task_id, "status": "Pending/In Queue"}
    elif task_result.state == 'SUCCESS':
        return {"task_id": task_id, "status": "Completed", "results": task_result.result}
    elif task_result.state == 'FAILURE':
        return {"task_id": task_id, "status": "Failed", "error": str(task_result.info)}
    else:
        return {"task_id": task_id, "status": task_result.state}