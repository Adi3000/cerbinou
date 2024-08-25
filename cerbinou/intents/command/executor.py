from datetime import datetime
from command.intent import Speech
from command.prompt import get_prompt_response
import logging

logger = logging.getLogger(__name__)

def get_time_speech(): 
    now = datetime.now()
    current_time = now.strftime("%H heures %M et %S secondes")
    return Speech(text= f"Il est {current_time}")

def get_misunderstood_speech():
    return Speech(text= "Je n'ai pas compris")

def get_prompt_speech(prompt: str):
    response= get_prompt_response(prompt)
    return Speech(text= response)