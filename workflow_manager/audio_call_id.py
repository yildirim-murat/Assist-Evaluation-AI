import httpx
import os
from dotenv import load_dotenv
from fastapi import HTTPException, status

load_dotenv()

AUDIO_URL = os.getenv("AUDIO_URL")

AUDIO_URL = AUDIO_URL + "/webresources/ses/getKayitDetay"

HTTP_TIMEOUT = 10.0

def get_audio_list_id(ucid: str, token: str ):
    
    params = {
        "token": token,
        "ucid": ucid,
        "classified": 1,
        "incidentId": "82998046",
        "isEngelsiz": "false"
    }

    headers = {
        "User-Agent": "curl/7.85.0",
        "Accept": "*/*"
    }

    with httpx.Client(headers=headers) as client:
        response = client.get(AUDIO_URL, params=params)

    data = response.json() #.get("data", [])
    ucid_list = [item["UCID"] for item in data if "UCID" in item]

    return {
        "UCID list": data
    }