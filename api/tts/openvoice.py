import httpx
import httpcore
import logging
import os
from audit import telegram
import random

OPENVOICE_API_URL = os.getenv("OPENVOICE_API_URL", "http://localhost:8381")
OPENVOICE_API_FAILBACK_URL = os.getenv("OPENVOICE_API_FAILBACK_URL", "http://localhost:5000")

logger = logging.getLogger(__name__)

error_files = [
    "Radio1.wav",
    "Radio2.wav",
    "Radio3.wav",
    "Vinyl10.wav",
    "Vinyl11.wav",
    "Vinyl12.wav",
    "Vinyl4.wav"
]

def speech(text: str):
    openvoice_param = {
        "model":"FR",
        "input": text,
        "speed":1.0,
        "response_format":"bytes",
        "voice":"cerbinou"
    }
    try:
        response = httpx.post(url=f"{OPENVOICE_API_URL}/v2/generate-audio", json=openvoice_param, timeout=(5,20))
        logging.info("tts [%s] response [%d]", OPENVOICE_API_URL, response.status_code)
        response.raise_for_status()
        telegram.send_message(text=text, quote=False)
        return response.content
    except (httpx.TimeoutException, httpx.ReadError) as err:
        logging.info("tts timeout from [%s] response from : %s\n%s", f"{OPENVOICE_API_URL}/v2/generate-audio", OPENVOICE_API_FAILBACK_URL, err)
        telegram.send_message(text=f" Error : <{text}>", quote=False)
        return error_response()



def error_response(): 
    track = error_files[random.randint(0, len(error_files) - 1)]
    current_dir = os.getcwd()
    with open(f"tts/effects/{track}", "rb") as f:
        binary_data = f.read()
        return binary_data