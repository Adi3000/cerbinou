import paho.mqtt.client as mqtt
from paho.mqtt.client import MQTTMessage, Client
import logging
import os

logger = logging.getLogger(__name__)

RHASSPY_SITE_ID = os.getenv("RHASSPY_SITE_ID", "default")

# Define the callback function for when a message is received
def on_message(client: Client, userdata: any, message: MQTTMessage):
    toggleMessage = "{\"siteId\": \""+ RHASSPY_SITE_ID +"\", \"reason\": \"ttsSay\" }"
    if message.topic == "hermes/tts/say":
        logger.info("Shutdown asr and hotword ")
        client.publish("hermes/asr/toggleOff", toggleMessage)
        client.publish( "hermes/hotword/toggleOff",toggleMessage)
    elif message.topic == "hermes/tts/sayFinished":
        logger.info("Re-enable asr and hotword ")
        client.publish("hermes/asr/toggleOn", toggleMessage)
        client.publish( "hermes/hotword/toggleOn",toggleMessage)
            
def tts_over_command_connection(broker_address: str, broker_port: int):

    # Create an MQTT client instance
    client = mqtt.Client()
    client.on_message = on_message
    client.connect(broker_address, broker_port)
    client.subscribe([("hermes/tts/say", 0) ,("hermes/tts/sayFinished", 0)])
    
    return client

