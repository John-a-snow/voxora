FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8001

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY app/ ./app/
COPY data/ ./data/
COPY scripts/ ./scripts/
COPY onnx/ ./onnx/

RUN python -c "from huggingface_hub import hf_hub_download; hf_hub_download(repo_id='Xenova/multilingual-e5-small', filename='onnx/model_int8.onnx', local_dir='/tmp/e5'); import os; os.makedirs('/app/onnx', exist_ok=True); os.replace('/tmp/e5/onnx/model_int8.onnx', '/app/onnx/model_int8.onnx')"

EXPOSE 8001

CMD ["python", "scripts/serve.py"]