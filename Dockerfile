FROM python:3.11-slim

ENV PYTHONDOMTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8001

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essentail \
    curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu

 
 requirements.txt .
pip install --no-cache-dir -r requirements.txt

 app/ .app/
 data/ ./data/
 scripts/ ./scripts/

SE 8001

["python", "scripts/serve.py"]