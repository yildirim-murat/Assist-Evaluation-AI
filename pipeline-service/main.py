from fastapi import FastAPI, UploadFile, File, HTTPException
import requests
import os
import tempfile
import re

app = FastAPI()

SPLIT_BASE = os.getenv("SPLIT_BASE", "http://split-service:8000")
WHISPER_BASE = os.getenv("WHISPER_BASE", "http://whisper-service:8001")

SPLIT_URL = f"{SPLIT_BASE}/split-audio/"
WHISPER_URL = f"{WHISPER_BASE}/transcribe-chunks/"

ID_RE = re.compile(r"^\d{15}$")


@app.post("/transcribe-audio/")
async def transcribe_audio(file: UploadFile = File(...)):
    suffix = os.path.splitext(file.filename)[1]
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(await file.read())
        tmp_path = tmp.name

    try:
        with open(tmp_path, "rb") as f:
            files = {"file": (file.filename, f, file.content_type)}
            split_resp = requests.post(SPLIT_URL, files=files, timeout=120)
        split_resp.raise_for_status()
        split_json = split_resp.json()
        chunks = split_json["chunks"]

        whisper_resp = requests.post(WHISPER_URL, json=chunks, timeout=600)
        whisper_resp.raise_for_status()
        whisper_json = whisper_resp.json()

        final_text = " ".join(r.get("text", "") for r in whisper_json.get("results", []))
        return {"duration": split_json["duration"],"filename":file.filename, "chunks": chunks, "transcript": final_text}

    except requests.RequestException as e:
        await delete_chunks(file.filename[:-4])
        raise HTTPException(status_code=502, detail=f"Dış servis hatası: {e}")
    finally:
        try:
            os.remove(tmp_path)
            await delete_chunks(file.filename[:-4])
        except FileNotFoundError:
            pass

@app.delete("/chunks/{file_code}")
async def delete_chunks(file_code: str):

    if not ID_RE.fullmatch(file_code):
        raise HTTPException(status_code=400, detail="Geçersiz file_code")

    url = f"{SPLIT_BASE}/chunks/{file_code}"
    try:
        resp = requests.delete(url, timeout=30)
    except requests.RequestException as e:
        raise HTTPException(status_code=502, detail=f"split-service ulaşılamıyor: {e}")

    content_type = resp.headers.get("content-type", "")
    if resp.status_code == 200:
        return resp.json() if "application/json" in content_type else {"message": resp.text}

    if "application/json" in content_type:
        try:
            data = resp.json()
            raise HTTPException(status_code=resp.status_code, detail=data.get("detail", data))
        except ValueError:
            raise HTTPException(status_code=resp.status_code, detail=resp.text)
    else:
        raise HTTPException(status_code=resp.status_code, detail=resp.text)