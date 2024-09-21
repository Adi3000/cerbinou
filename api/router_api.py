from typing import Dict, Optional
from fastapi import FastAPI, Request, Response
from fastapi.responses import PlainTextResponse
import uvicorn
from intent.handle.commands import get_time_speech, get_misunderstood_speech, get_prompt_speech
from intent.classification.analyze import analyze_text
from intent.models import IntentResponse, IntentRequest
from intent.handle.nointent_consumer import nointent_connection
from hotword import handler
from tts.openvoice import speech
from asr.speech_to_text import parse_audio
from utils import LogRequestsMiddleware
import logging
import threading
import sys
import os

CERBINOU_PORT = int(os.getenv("CERBINOU_PORT", "9977"))
MQTT_HOST = os.getenv("MQTT_HOST", "localhost")
MQTT_PORT = int(os.getenv("MQTT_PORT", "12183"))

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'  # Define the log format
)
 
logger = logging.getLogger(__name__)
router = FastAPI()

@router.head("/api/health")
async def health_check():
    return {"status": "ok"}

@router.post("/api/asr/text", response_class=PlainTextResponse)
async def asr_decode(request: Request):
    logging.info("Received asr text request")
    if request.headers.get('Content-Type') != 'audio/wav' and request.headers.get('Content-Type') != 'audio/wave':
        return {"error": "Invalid content type. Only 'audio/wav' is accepted."}
    # Read the binary data from the request body
    audio_data = await request.body()
    return parse_audio(audio_data)

@router.post("/api/asr/transcript")
async def asr_transcript(request: Request):
    logging.info("Received transcript request")
    transcripted_text = await asr_decode(request)
    return { "text": transcripted_text, "transcribe_seconds": 0 }

@router.post("/api/intent/text")
async def text_decode(request: Request):
    logging.info("Received intent request")
    # Read the binary data from the request body
    intent_text_data = await request.body()
    intent_text = intent_text_data.decode()
    return analyze_text(intent_text)

@router.post("/api/command")
async def execute_command(request: IntentRequest):
    logger.info("Intent command %s", request.json())
    if request.intent.name == "GetTime":
        return IntentResponse(speech=get_time_speech())
    elif request.intent.name == "Prompt":
        return IntentResponse(speech=get_prompt_speech(request.text))
    else:
        return IntentResponse(speech=get_misunderstood_speech())


@router.post("/api/tts")
async def execute_command(request: Request):
    speech_data = await request.body()
    speech_text = speech_data.decode()
    logger.info("Speech request <%s>", speech_text)
    wav_data = speech(speech_text)
    return Response(content=wav_data, media_type="audio/wav")

if __name__ == "__main__":
    no_intent_mqtt: Optional[any] = None
    wake_handler: Optional[any] = None
    no_intent_consumer: Optional[any]
    try:
        no_intent_mqtt = nointent_connection(MQTT_HOST, MQTT_PORT)
        no_intent_consumer = threading.Thread(target=no_intent_mqtt.loop_forever)
        no_intent_consumer.start()
#        wake_handler = threading.Thread(target=handler.wake)
#        wake_handler.start()
        
    except ConnectionRefusedError:
        logging.warning("Cannot connect to %s:%d", MQTT_HOST, MQTT_PORT)
    router.add_middleware(LogRequestsMiddleware)
    uvicorn.run("router_api:router", host="0.0.0.0", port=CERBINOU_PORT, reload=False, log_level="info")
    
    
    handler.running = False
    if no_intent_mqtt:
        no_intent_mqtt.disconnect()
        no_intent_consumer.join()

#    wake_handler.join()
    sys.exit(0)
