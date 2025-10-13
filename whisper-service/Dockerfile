FROM nvidia/cuda:12.1.1-runtime-ubuntu22.04

ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
      python3 \
      python3-distutils \
      python3-pip \
      ffmpeg \
      git \
      libsndfile1 \
      ca-certificates \
      build-essential \
      curl && \
    ln -sf /usr/bin/python3 /usr/bin/python && \
    python3 -m pip install --upgrade pip setuptools wheel && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./

RUN python3 -m pip install --no-cache-dir \
      "torch" "torchvision" "torchaudio" --extra-index-url https://download.pytorch.org/whl/cu121 || \
    (echo "Torch install failed; continuing to install requirements to show real error" && true) && \
    python3 -m pip install --no-cache-dir -r requirements.txt


COPY . .

EXPOSE 8001
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001"]