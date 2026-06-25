FROM python:3.10-slim

WORKDIR /app

# Install system dependencies for OpenCV and ONNX
RUN apt-get update && apt-get install -y \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . ./worker

# Run the celery worker
CMD ["celery", "-A", "worker.celery_app", "worker", "--loglevel=info", "--pool=solo"]