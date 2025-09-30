import os
import httpx
from sqlalchemy import create_engine, Table, Column, Integer, String, Text, MetaData
from datetime import datetime

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@s_db_call_report:5432/call_report")
engine = create_engine(DATABASE_URL)
metadata = MetaData()

transcripts = Table(
    "transcripts",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("filename", String(255), nullable=False),
    Column("text", Text, nullable=False),
    Column("created_at", String, default=str(datetime.utcnow())),
)

metadata.create_all(engine)

def save_transcript(filename, text):
    with engine.begin() as conn:
        ins = transcripts.insert().values(filename=filename, text=text)
        conn.execute(ins)

async def get_transcriber():
    data_dir = "/app/data"
    files = [f for f in os.listdir(data_dir) if f.endswith(".wav")]

    results = []

    async with httpx.AsyncClient(timeout=60.0) as client:
        for file in files:
            file_path = os.path.join(data_dir, file)
            with open(file_path, "rb") as f:
                files_payload = {"file": (file, f, "audio/wav")}
                try:
                    resp = await client.post(
                        "http://pipeline-service:8002/transcribe-audio/",
                        files=files_payload
                    )
                    try:
                        result = resp.json()
                        transcript_text = result.get("transcript", "")
                    except ValueError:
                        print(f"Warning: {file} returned invalid JSON: {resp.text}")
                        transcript_text = ""
                except httpx.RequestError as e:
                    print(f"Request failed for {file}: {e}")
                    transcript_text = ""

                results.append({file: transcript_text})
                save_transcript(file, transcript_text)

    return {"Transcription": "OK!"}
