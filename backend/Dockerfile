# 1. Base image with Python
FROM python:3.10-slim

# 2. Install system deps
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
      ffmpeg \
      build-essential \
      git && \
    rm -rf /var/lib/apt/lists/*

# 3. Set working dir
WORKDIR /app

# 4. Copy & install Python deps
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copy our source code
COPY app ./app

# 6. Expose the port FastAPI runs on
EXPOSE 8000

# 7. Run Uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
