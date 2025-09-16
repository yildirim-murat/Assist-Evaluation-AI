from fastapi import FastAPI, UploadFile, File
import whisper
import os

app = FastAPI()
model = whisper.load_model("turbo")

CHUNK_DIR = "chunks"

@app.post("/transcribe-chunks/")
async def transcribe_chunks(filenames: list[str]):
    results = []
    for filename in filenames:
        path = os.path.join(CHUNK_DIR, filename)
        result = model.transcribe(path, language="tr")
        results.append({"file": filename, "text": result["text"]})
    return {"results": results}
