FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt ./
RUN apt-get update && apt-get install -y build-essential poppler-utils tesseract-ocr libgl1 ffmpeg && \
    pip install --no-cache-dir -r requirements.txt
COPY . /app
ENV PYTHONUNBUFFERED=1
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
