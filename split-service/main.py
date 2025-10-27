from fastapi import FastAPI, UploadFile, File, HTTPException
from pathlib import Path
import subprocess
import os
import re

app = FastAPI()

CHUNK_DIR = Path("chunks")

os.makedirs(CHUNK_DIR, exist_ok=True)
ID_RE = re.compile(r"^\d{15}$")

@app.post("/split-audio/")
async def split_audio(file: UploadFile = File(...)):
    input_path = f"temp_{file.filename}"
    with open(input_path, "wb") as f:
        f.write(await file.read())

    file_code = os.path.splitext(file.filename)[0]

    converted_path = "converted.wav"

    subprocess.run([
        "ffmpeg", "-i", input_path,
        "-ar", "16000", "-ac", "1",
        converted_path, "-y"
    ])

    result = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries",
         "format=duration", "-of",
         "default=noprint_wrappers=1:nokey=1",
         converted_path],
         stdout=subprocess.PIPE,
         stderr=subprocess.STDOUT
         )

    duration = float(result.stdout)

    chunk_files = []
    step = 30
    overlap = 2
    start = 0
    chunk_index = 1
    while start < duration:
        end = min(start + step + overlap, duration)
        chunk_filename = f"{file_code}_{chunk_index}.wav"
        chunk_path = os.path.join(CHUNK_DIR, chunk_filename)

        subprocess.run([
            "ffmpeg", "-i", converted_path,
            "-ss", str(start), "-to", str(end),
            "-ar", "16000", "-ac", "1",
            chunk_path, "-y"
        ], check=True)

        chunk_files.append(chunk_filename)
        start += step
        chunk_index += 1

    os.remove(input_path)
    os.remove(converted_path)

    return {"chunks": chunk_files, "duration": duration}


@app.delete("/chunks/{file_code}")
async def delete_chunks(file_code: str):
    if not ID_RE.fullmatch(file_code):
        raise HTTPException(status_code=400, detail="Geçersiz file_code")

    matches = list(CHUNK_DIR.glob(f"{file_code}_*.wav"))

    deleted, errors = [], []
    for p in matches:
        try:
            p.unlink()
            deleted.append(p.name)
        except Exception as e:
            errors.append({"file": p.name, "error": str(e)})


    if not deleted and not errors:
        raise HTTPException(status_code=404, detail="Parça bulunamadı")

    return {"deleted_count": len(deleted), "deleted": deleted, "errors": errors}
