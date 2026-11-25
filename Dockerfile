FROM python:3.12-slim

WORKDIR /app

ENV HF_HOME=/tmp/hf_cache \
    TRANSFORMERS_CACHE=/tmp/hf_cache \
    TORCH_HOME=/tmp/torch_cache \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=7860

RUN mkdir -p /tmp/hf_cache /tmp/torch_cache && chmod -R 777 /tmp/hf_cache /tmp/torch_cache

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Install CPU-only PyTorch to fit comfortably inside Hugging Face Spaces Free 16GB RAM Tier
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu && \
    pip install --no-cache-dir \
    "fastapi>=0.100.0" \
    "uvicorn[standard]>=0.22.0" \
    "pydantic>=2.0.0" \
    "sqlalchemy>=2.0.0" \
    "geopy>=2.3.0" \
    "numpy>=1.24.0" \
    "scikit-learn>=1.3.0" \
    "scipy>=1.10.0" \
    "python-multipart>=0.0.6" \
    "httpx>=0.27.0" \
    "python-dotenv>=1.0.0" \
    "transformers>=4.40.0" \
    "lightgbm>=4.0.0" \
    "huggingface_hub>=0.25.0" \
    "pandas>=2.0.0" \
    "pyarrow>=14.0.0" \
    "rank-bm25>=0.2.2" \
    "pillow>=10.0.0"

COPY backend ./backend
COPY frontend/dist ./frontend/dist

EXPOSE 7860

CMD ["uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "7860"]
