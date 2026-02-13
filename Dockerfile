FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1
WORKDIR /app

# Install system deps sometimes required by gradio (kept minimal)
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       build-essential \
       gcc \
       libsndfile1 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy app files
COPY . /app

# Ensure output dir exists
RUN mkdir -p /app/output

EXPOSE 7860 7861

CMD ["python", "main.py"]
