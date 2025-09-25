import httpx
import os
from dotenv import load_dotenv
from fastapi import HTTPException, status

load_dotenv()

AUDIO_URL = os.getenv("AUDIO_URL")

AUDIO_URL = AUDIO_URL + "/webresources/ses/getKayit"

HTTP_TIMEOUT = 10.0

def get_selected_list_audio(token: str):
    
    params = {
        "token": token,
        "baslangicTar": "2025-06-01",
        "baslangicSaat": "00:00",
        "bitisTar": "2025-06-01",
        "bitisSaat": "00:01",
        "callId": "",
        "arayanNumara": "",
        "arananNumara": "",
        "callType": "0",
        "agentid": "0",
        "vakaId": "",
        "crsAramasi": "0"
    }

    headers = {
        "User-Agent": "curl/7.85.0",
        "Accept": "*/*"
    }

    with httpx.Client(headers=headers) as client:
        response = client.get(AUDIO_URL, params=params)

    data = response.json().get("data", [])
    ucid_list = [item["UCID"] for item in data if "UCID" in item]

    return {
        "UCID list": ucid_list
    }