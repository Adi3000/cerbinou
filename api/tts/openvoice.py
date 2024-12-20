import httpx
import httpcore
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
        response = httpx.post(url=f"{OPENVOICE_API_URL}/v2/generate-audio", json=openvoice_param, timeout=(2,30))
        logging.info("tts [%s] response", OPENVOICE_API_URL)
    except (httpx.TimeoutException, httpx.ReadError) as err:
        response = httpx.post(url=f"{OPENVOICE_API_FAILBACK_URL}/v2/generate-audio", json=openvoice_param, timeout=(2,120))
        logging.info("timeout from [%s] response from : %s\n%s", f"{OPENVOICE_API_URL}/v2/generate-audio", OPENVOICE_API_FAILBACK_URL, err)
    telegram.send_message(text=text, quote=False)
    return response.content


