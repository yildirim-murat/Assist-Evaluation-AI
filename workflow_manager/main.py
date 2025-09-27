from fastapi import FastAPI
from token_handler import get_token
from audio_selector import get_selected_list_audio
from audio_call_id import get_audio_list_id
from audio_downloader import get_audio_downloader
from transcriber import get_transcriber
from sentiment_analysis import get_sentiment_analysis
from ai_evaluator import get_ai_evaluator
from token_handler import get_is_active

app = FastAPI(title="Workflow Manager", version="1.0.0")

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.get("/transcrip")
async def start_transcrip():
    return await get_transcriber()

@app.get("/strt")
async def start_workflow():
    is_active = get_is_active()
    if not is_active:
        return {"status": "Service is not active"}
    token = get_token()
    get_list_audio_ucid = get_selected_list_audio("b9c162c3-1c4d-43af-8dd1-aa26633e8b9a")
    get_list_id = get_audio_list_id({get_list_audio_ucid['UCID list'][0]}, "b9c162c3-1c4d-43af-8dd1-aa26633e8b9a")
    audio_downloader = get_audio_downloader(get_list_id)
    transcribe_to_audio = get_transcriber()
    sentiment_analysis = get_sentiment_analysis()
    model_integration = get_ai_evaluator()
    spring_boot_integration = "OK -- Spring boot'a kaydedildi"
    
    return {
        "status": is_active,
        "token": token,
        "select_audio": f"select_audio elemani sayısı: {len(get_list_audio_ucid['UCID list'])}",
        "get_list_id_send_to_file_name": f"get_list_id {get_list_audio_ucid['UCID list'][0]}",
        "get_list_id": f"get_list_id {get_list_id}",
        "audio_downloader": audio_downloader, "transcribe_to_audio": transcribe_to_audio, 
        "sentiment_analysis": sentiment_analysis, "model_integration": model_integration, 
        "spring_boot_integration": spring_boot_integration
           }

@app.get("/create_token")
def create_token_endpoint(username: str, password: str):
    from token_handler import create_token
    import asyncio
    response = asyncio.run(create_token(username, password))
    return {
            "token" : response.raw.get("token", "Token creation failed")
        }