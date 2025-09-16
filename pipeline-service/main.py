from fastapi import FastAPI, UploadFile, File
import requests
import os
import tempfile

app = FastAPI()

SPLIT_URL = "http://split-service:8000/split-audio/"
WHISPER_URL = "http://whisper-service:8001/transcribe-chunks/"

@app.post("/transcribe-audio/")
async def transcribe_audio(file: UploadFile = File(...)):
    # 1️⃣ Geçici dosyaya kaydet
    suffix = os.path.splitext(file.filename)[1]
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(await file.read())
        tmp_path = tmp.name

    try:
        # 2️⃣ Split-service'e gönder
        with open(tmp_path, "rb") as f:
            files = {"file": (file.filename, f, file.content_type)}
            split_resp = requests.post(SPLIT_URL, files=files).json()
        
        chunks = split_resp["chunks"]

        # 3️⃣ Whisper-service'e gönder
        whisper_resp = requests.post(WHISPER_URL, json=chunks).json()

        # 4️⃣ Transcriptleri birleştir
        final_text = " ".join([r["text"] for r in whisper_resp["results"]])

    finally:
        # 5️⃣ Geçici dosyayı sil
        os.remove(tmp_path)

    return {
        "duration": split_resp["duration"],
        "chunks": chunks,
        "transcript": final_text
    }