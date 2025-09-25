import os
import requests
import httpx
import logging
from dotenv import load_dotenv
from pydantic import BaseModel
from typing import Dict, Any
from fastapi import HTTPException, status
import json

load_dotenv()

AUDIO_URL = os.getenv("AUDIO_URL")
AUDIO_USERNAME = os.getenv("AUDIO_USERNAME")
AUDIO_PASSWORD = os.getenv("AUDIO_PASSWORD")
BACKEND_URL = os.getenv("BACKEND_URL")

AUDIO_URL = AUDIO_URL + "/webresources/ses/login"

HTTP_TIMEOUT = 10.0

logger = logging.getLogger("ses_login")
logging.basicConfig(level=logging.INFO)

class ServiceResponseDTO(BaseModel):
    key: str
    value: str
    status_code: int

class LoginRequest(BaseModel):
    username: str
    password: str

class ExternalLoginResponse(BaseModel):
    raw: Dict[str, Any]
    status_code: int

def get_last_token() -> ServiceResponseDTO:
    url = BACKEND_URL + "/api/v1/system"
    params = {"key": "token"}
    response = requests.get(url, params=params, timeout=HTTP_TIMEOUT)
    data = response.json()
    return ServiceResponseDTO(
        key="token",
        value=data.get("data"),
        status_code=response.status_code
    )

def get_token() -> dict:
    token_dto = get_last_token()
    return {"token": token_dto.value, "status_code": token_dto.status_code}

def get_is_active() -> bool:
    url = BACKEND_URL + "/api/v1/system"
    params = {"key": "active"}
    response = requests.get(url, params=params, timeout=HTTP_TIMEOUT)
    data = response.json()
    return data.get("data", False)


async def create_token(username: str, password: str, verify_ssl: bool = True) -> ExternalLoginResponse:
    payload = {"username": username, "password": password}
    headers = {"Content-Type": "application/json"}

    async with httpx.AsyncClient(timeout=HTTP_TIMEOUT, verify=verify_ssl) as client:
        try:
            resp = await client.post(AUDIO_URL, json=payload, headers=headers)
        except httpx.RequestError as exc:
            logger.error("HTTP request error while contacting SES: %s", exc)
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"SES service unreachable: {exc}"
            )

        # parse JSON regardless of content-type
        try:
            body = resp.json()
        except ValueError:
            try:
                body = json.loads(resp.text)
            except Exception:
                body = {"text": resp.text}

        if resp.status_code >= 400:
            logger.warning("SES login returned status %s, body: %s", resp.status_code, body)
            return ExternalLoginResponse(raw={"status": "error", "body": body}, status_code=resp.status_code)

        return ExternalLoginResponse(raw=body, status_code=resp.status_code)