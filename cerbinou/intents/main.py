from typing import Dict
from fastapi import FastAPI
import uvicorn
from command.executor import get_time_speech, get_misunderstood_speech, get_prompt_speech
from command.intent import IntentResponse, IntentRequest
from command.nointent_consumer import nointent_connection
from utils import LogRequestsMiddleware
import logging
import threading
import sys
import os

CERBINOU_PORT = int(os.getenv("CERBINOU_PORT", "8000"))
MQTT_HOST = os.getenv("MQTT_HOST", "localhost")
MQTT_PORT = int(os.getenv("MQTT_HOST", "12183"))

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'  # Define the log format
)
    
logger = logging.getLogger(__name__)
app = FastAPI()

@app.post("/api/command")
def execute_command(request: IntentRequest): 
    logger.info("Message output %s", request.json())
    match request.intent.name:
        case "GetTime":
            return IntentResponse(speech=get_time_speech())
        case "Prompt":
            return IntentResponse(speech=get_prompt_speech(request.text))
        case _:
            return IntentResponse(speech=get_misunderstood_speech())


if __name__ == "__main__":
    no_intent_mqtt = nointent_connection(MQTT_HOST, MQTT_PORT)
    no_intent_consumer = threading.Thread(target=no_intent_mqtt.loop_forever)
    no_intent_consumer.start()
    app.add_middleware(LogRequestsMiddleware)
    uvicorn.run("main:app", host="0.0.0.0", port=CERBINOU_PORT, reload=False, log_level="info")
    no_intent_mqtt.disconnect()  # Disconnect the MQTT client
    no_intent_consumer.join()    # Wait for the thread to finish
    sys.exit(0)                  # Exit the program
