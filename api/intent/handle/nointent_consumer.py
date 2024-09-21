import paho.mqtt.client as mqtt
from paho.mqtt.client import MQTTMessage, Client
from intent.models import NoIntent, ParsedIntent, IntentType, IntentMQTT
import json
import logging

logger = logging.getLogger(__name__)
client = mqtt.Client()

# Define the callback function for when a message is received
def on_message(client: Client, userdata: any, message: MQTTMessage):
    no_intent_json = json.loads(message.payload.decode())
    no_intent = NoIntent(** no_intent_json)
    parsed_intent = ParsedIntent(
        input= no_intent.input,
        intent= IntentType(intentName="Prompt", confidenceScore=1),
        id= no_intent.id,
        sessionId= no_intent.sessionId,
        siteId= no_intent.siteId
    )
    final_intent = IntentMQTT(
        input= no_intent.input,
        intent= IntentType(intentName="Prompt", confidenceScore=1),
        id= no_intent.id,
        sessionId= no_intent.sessionId,
        siteId= no_intent.siteId,
        rawInput=no_intent.input,
        raw_text=no_intent.input,
        text=no_intent.input
    )
    logger.info("Forwarding message: %s from topic %s", parsed_intent.json(), message.topic)
    client.publish("hermes/nlu/intentParsed", parsed_intent.json())
    client.publish("hermes/intent/Prompt", final_intent.json())
            
def nointent_connection(broker_address: str, broker_port: int):

    # Create an MQTT client instance
    client = mqtt.Client()
    # Set the callbacks
    client.on_message = on_message
    client.connect(broker_address, broker_port)
    # Subscribe to Hermes intent topics
    topic = "hermes/nlu/intentNotRecognized"  # Replace with the topic you want to subscribe to
    client.subscribe(topic)
    
    return client