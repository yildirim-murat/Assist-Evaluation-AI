from fastapi import FastAPI, UploadFile, File
import subprocess
import os

app = FastAPI()

CHUNK_DIR = "chunks"

os.makedirs(CHUNK_DIR, exist_ok=True)

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