FROM python:3.10-slim

WORKDIR /app

# ffmpeg yükle (ses dönüştürme için)
RUN apt-get update && apt-get install -y ffmpeg && rm -rf /var/lib/apt/lists/*

# Python bağımlılıklarını yükle
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Uygulama dosyalarını kopyala
COPY . .

# chunks klasörünü container içinde oluştur
RUN mkdir -p /app/chunks

# FastAPI server başlat
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
