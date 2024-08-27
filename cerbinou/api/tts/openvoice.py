import requests
import logging
import os

OPENVOICE_API_URL = os.getenv("OPENVOICE_API_URL", "http://localhost:5000/convert/tts")
OPENVOICE_API_FAILBACK_URL = os.getenv("OPENVOICE_API_FAILBACK_URL", "http://localhost:5000/convert/tts")

logger = logging.getLogger(__name__)

def speech(text: str):
    openvoice_param = {
        "model":"FR",
        "input": text,
        "speed":1.0,
        "response_format":"bytes",
        "voice":"cerbinou"
    }
    response = requests.post(url=OPENVOICE_API_URL, data=openvoice_param, timeout=(2,30))
    logging.info("whisper [%s] response : %s", OPENVOICE_API_URL, response.text)

    return response.content


