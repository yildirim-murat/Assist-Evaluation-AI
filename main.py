from fastapi import FastAPI, UploadFile, File
import subprocess
import os
import whisper

app = FastAPI()

CHUNK_DIR = "chunks"
os.makedirs(CHUNK_DIR, exist_ok=True)

# Whisper modelini yükle
model = whisper.load_model("base")


@app.post("/transcribe-audio/")
async def transcribe_audio(file: UploadFile = File(...)):
    input_path = f"temp_{file.filename}"
    with open(input_path, "wb") as f:
        f.write(await file.read())

    file_code = os.path.splitext(file.filename)[0]

    # 1️⃣ WAV formatına çevir (mono, 16kHz)
    converted_path = "converted.wav"
    subprocess.run([
        "ffmpeg", "-i", input_path,
        "-ar", "16000", "-ac", "1",
        converted_path, "-y"
    ])

    # 2️⃣ Sesin toplam süresini al
    result = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries",
         "format=duration", "-of",
         "default=noprint_wrappers=1:nokey=1", converted_path],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT
    )
    duration = float(result.stdout)

    # 3️⃣ Parçalara böl (30 sn + 2 sn overlap)
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
        ])

        chunk_files.append(chunk_path)
        start += step
        chunk_index += 1

    # 4️⃣ Her chunk için Whisper transkripti al
    transcripts = []
    for chunk in chunk_files:
        result = model.transcribe(chunk, language="tr")
        transcripts.append(result["text"])

    # 5️⃣ Temizlik
    os.remove(input_path)
    os.remove(converted_path)
    # istersen chunk dosyalarını da silebilirsin
    # for c in chunk_files:
    #     os.remove(c)

    # 6️⃣ Tüm parçaları birleştir
    final_transcript = " ".join(transcripts)

    return {
        "duration": duration,
        "chunks": [os.path.basename(c) for c in chunk_files],
        "transcript": final_transcript
    }
