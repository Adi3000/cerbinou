import requests
import random
import string
import logging
import os

WHISPER_URL = os.getenv("WHISPER_URL", "http://localhost:9000/asr")
WHISPER_FALLBACK_URL = os.getenv("WHISPER_FALLBACK_URL", "http://localhost:9000/asr")


logger = logging.getLogger(__name__)

def parse_audio(audio_data: bytes):
    # Define the file path (you can customize the filename)
    random_filename = ''.join(random.choices(string.ascii_letters + string.digits, k=12)) + ".wav"
    files_to_forward = {
        "audio_file": (random_filename,audio_data, "audio/wav")
    }
    whisper_query_param = {
        "encode" : "true",
        "task": "transcribe",
        "language" : "fr",
        "word_timestamps" : False,
        "output" : "txt"
    }
    try:
        response = requests.post(url=WHISPER_URL, files=files_to_forward, data=whisper_query_param, timeout=(2,30))
        logging.info("whisper [%s] response : %s", WHISPER_URL, response.text)
    except requests.exceptions.Timeout:
        response = requests.post(url=WHISPER_FALLBACK_URL, files=files_to_forward, data=whisper_query_param)
    except requests.exceptions.ConnectionError:
        response = requests.post(url=WHISPER_FALLBACK_URL, files=files_to_forward, data=whisper_query_param)

    return response.text


