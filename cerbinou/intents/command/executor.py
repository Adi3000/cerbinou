from datetime import datetime
from command.intent import Speech
import logging
import requests

logger = logging.getLogger(__name__)

def get_time_speech(): 
    now = datetime.now()
    current_time = now.strftime("%H heures %M et %S secondes")
    return Speech(text= f"Il est {current_time}")

def get_misunderstood_speech():
    return Speech(text= "Je n'ai pas compris")

def get_prompt_speech(prompt: str):
    response= requests.post("http://localhost:8080/completion", json= {"prompt": prompt})
    return Speech(text= response.json().content)