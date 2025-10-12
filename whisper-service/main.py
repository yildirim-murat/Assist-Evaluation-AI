from fastapi import FastAPI, UploadFile, File
import whisper
import os

app = FastAPI()

model_name = os.getenv("WHISPER_MODEL", "").strip()

if not model_name:
    model_name = "small"

print(f"Loading Whisper model: {model_name}")

model = whisper.load_model(model_name, device="cuda")

CHUNK_DIR = "chunks"

@app.post("/transcribe-chunks/")
async def transcribe_chunks(filenames: list[str]):
    results = []
    for filename in filenames:
        path = os.path.join(CHUNK_DIR, filename)
        result = model.transcribe(path, language="tr")
        results.append({"file": filename, "text": result["text"]})
    return {"results": results}
