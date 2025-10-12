FROM nvidia/cuda:12.1.1-runtime-ubuntu22.04

ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends &&\
      python3.10 python3.10-distutils python3-pip ffmpeg git libsndfile1 && \
    ln -sf /usr/bin/python3.10 /usr/bin/python3 && \
    python3 -m pip install --upgrade pip setuptools wheel && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN python3 -m pip install --no-cache-dir \
      torch torchvision torchaudio --extra-index-url https://download.pytorch.org/whl/cu121 && \
    python3 -m pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001"]