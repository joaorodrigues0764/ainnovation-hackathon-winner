# API FastAPI + RAG. Construir a partir da raiz: docker compose build api
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# EMBEDDINGS=0 dá uma imagem pequena e rápida (só BM25); 1 instala o torch de CPU (~1 GB a mais)
ARG EMBEDDINGS=1
COPY requirements.txt .
RUN if [ "$EMBEDDINGS" = "1" ]; then \
        pip install torch --index-url https://download.pytorch.org/whl/cpu && \
        pip install -r requirements.txt; \
    else \
        grep -v '^sentence-transformers' requirements.txt > /tmp/req.txt && pip install -r /tmp/req.txt; \
    fi

COPY . .
# a pasta da cache existe na imagem para o volume herdar o dono (senão fica de root)
RUN useradd --create-home app && mkdir -p /home/app/.cache/huggingface \
    && chown -R app /app /home/app/.cache
USER app

ENV USE_EMBEDDINGS=$EMBEDDINGS \
    HF_HOME=/home/app/.cache/huggingface

EXPOSE 8000
# no 1.º arranque com embeddings descarrega o modelo (~470 MB): dar até ~10 min
HEALTHCHECK --interval=10s --timeout=5s --start-period=60s --retries=60 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health', timeout=4)"
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]
