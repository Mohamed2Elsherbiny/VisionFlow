# VisionFlow

**Event-Driven Real-Time Video Analytics Pipeline**

VisionFlow is a scalable, microservices-based computer vision platform designed for real-time video analytics. By decoupling API ingestion from computationally intensive object detection workloads, VisionFlow delivers high concurrency, fault tolerance, and responsive performance even under heavy video stream traffic.

Built with FastAPI, Celery, Redis, ONNX Runtime, and YOLOv7, the system provides an asynchronous processing architecture suitable for production-grade computer vision deployments.

---

## Overview

Traditional computer vision APIs often perform inference synchronously, forcing clients to wait while deep learning models process incoming frames. This approach quickly becomes a bottleneck when handling multiple streams or high-resolution video data.

VisionFlow solves this challenge through an event-driven architecture:

1. Frames are received by a lightweight API.
2. Tasks are immediately queued through Redis.
3. Celery workers process inference asynchronously.
4. Results are retrieved independently using task identifiers.

This architecture ensures that API responsiveness remains consistent regardless of inference latency.

---

## Key Features

### Asynchronous Processing

* Non-blocking API design
* Instant task submission
* Background inference execution

### Scalable Architecture

* Horizontally scalable worker nodes
* Distributed task queue management
* Fault-tolerant message delivery

### Production-Ready Computer Vision

* YOLOv7 object detection
* ONNX Runtime acceleration
* CPU and GPU execution support

### Containerized Deployment

* Docker Compose orchestration
* Isolated microservices
* Portable deployment across environments

---

## System Components

### 1. FastAPI Ingestion Layer

The API service is responsible for:

* Validating incoming requests
* Receiving image frames
* Encoding image data
* Creating asynchronous processing tasks
* Returning task identifiers immediately

#### Workflow

1. Receive image frame
2. Validate payload
3. Encode image as Base64
4. Dispatch Celery task
5. Return `task_id`

This design prevents inference workloads from blocking client requests.

---

### 2. Redis Broker & Result Backend

Redis serves two critical functions:

#### Message Broker

```text
redis://redis:6379/0
```

Responsibilities:

* Queue incoming tasks
* Handle message delivery
* Prevent task loss during traffic spikes

#### State Backend

```text
redis://redis:6379/1
```

Stores:

* Task status
* Processing state
* Detection results
* Failure information

Task states include:

* PENDING
* SUCCESS
* FAILURE

---

### 3. Celery Worker

The worker service performs all object detection operations.

Responsibilities:

* Poll Redis queue
* Decode image payloads
* Preprocess frames
* Execute inference
* Store detection metadata

---

### 4. ONNX Runtime Inference Engine

To maximize portability and performance, the YOLOv7 model is exported to ONNX format.

#### Preprocessing Pipeline

```text
Image
  ↓
Resize (640x640)
  ↓
Normalize
  ↓
Transpose (CHW)
  ↓
ONNX Runtime
  ↓
Detections
```

#### Hardware Compatibility

The runtime automatically supports:

* NVIDIA CUDA execution
* GPU acceleration
* CPU fallback execution

allowing deployment across diverse hardware environments.

---

## API Endpoints

### Analyze Frame

#### POST `/analyze-frame/`

Submits an image for asynchronous analysis.

#### Response

```json
{
  "task_id": "8f4a0e2c-58e4-4c8a-a6fd-2c3b18bfc1e1"
}
```

---

### Retrieve Results

#### GET `/tasks/{task_id}`

Returns the processing status and detection results.

#### Example Response

```json
{
  "status": "SUCCESS",
  "detections": [
    {
      "class": "person",
      "confidence": 0.97,
      "bbox": [120, 85, 340, 610]
    }
  ]
}
```

---

## Technology Stack

| Component         | Technology     |
| ----------------- | -------------- |
| API Framework     | FastAPI        |
| Task Queue        | Celery         |
| Message Broker    | Redis          |
| State Backend     | Redis          |
| Computer Vision   | YOLOv7         |
| Inference Runtime | ONNX Runtime   |
| Image Processing  | OpenCV         |
| Containerization  | Docker         |
| Orchestration     | Docker Compose |

---

## Deployment

### Docker Compose Architecture

The entire stack is deployed using Docker Compose.

Services include:

```text
visionflow-api
redis
visionflow-worker
```

Benefits:

* Simple deployment
* Reproducible environments
* Service isolation
* Rapid scaling

---

## Dependency Isolation

The API and worker services run in separate containers using lightweight Python 3.10 Slim images.

Worker containers include additional system dependencies required by OpenCV:

```text
libglib2.0-0
libsm6
```

This separation avoids dependency conflicts while keeping images minimal.

---

## Model Management

To keep images lightweight, trained models are not bundled into container images.

Instead, models are mounted using Docker volumes:

```yaml
volumes:
  - ./models:/app/models
```

Benefits:

* Hot-swappable models
* Faster deployments
* Smaller image sizes
* No rebuild required after model updates

---

## Python Package Resolution

To ensure Celery correctly discovers worker modules, VisionFlow follows two best practices:

### Package Initialization

```text
worker/
└── __init__.py
```

This explicitly marks the worker directory as a Python package.

### PYTHONPATH Configuration

```dockerfile
ENV PYTHONPATH=/app
```

This guarantees reliable absolute imports inside containers and prevents module resolution errors during worker startup.

---

## Scalability Benefits

VisionFlow's architecture provides:

* High request concurrency
* Fault-tolerant task processing
* Independent worker scaling
* Efficient resource utilization
* Resilient distributed processing

Because inference occurs outside the API process, web responsiveness remains stable even during heavy computational workloads.

---

## Future Enhancements

Potential roadmap items include:

* Multi-camera stream management
* Real-time event notifications
* Object tracking support
* Kafka integration
* Distributed worker autoscaling
* Model version management
* Kubernetes deployment support
* Edge inference deployment
