import requests
import logging
import os
from audit import telegram
OPENVOICE_API_URL = os.getenv("OPENVOICE_API_URL", "http://localhost:8381")
OPENVOICE_API_FAILBACK_URL = os.getenv("OPENVOICE_API_FAILBACK_URL", "http://localhost:5000")

logger = logging.getLogger(__name__)

def speech(text: str):
    openvoice_param = {
        "model":"FR",
        "input": text,
        "speed":1.0,
        "response_format":"bytes",
        "voice":"cerbinou"
    }
    try:
        response = requests.post(url=f"{OPENVOICE_API_URL}/v2/generate-audio", json=openvoice_param, timeout=(2,30))
        logging.info("tts [%s] response", OPENVOICE_API_URL)
    except requests.exceptions.Timeout:
        response = requests.post(url=f"{OPENVOICE_API_FAILBACK_URL}/v2/generate-audio", json=openvoice_param)
        logging.info("timeout from [%s] response from : %s", f"{OPENVOICE_API_URL}/v2/generate-audio", OPENVOICE_API_FAILBACK_URL)
    except requests.exceptions.ConnectionError:
        response = requests.post(url=f"{OPENVOICE_API_FAILBACK_URL}/v2/generate-audio", json=openvoice_param)
        logging.info("connection refuse to[%s] response from : %s",OPENVOICE_API_URL, OPENVOICE_API_FAILBACK_URL)
    telegram.send_message(text=text, quote=True)
    return response.content


