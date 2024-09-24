from datetime import datetime
import requests
import logging  
import re
import json
import os
from audit import telegram
from intent.handle.weather import task

LLAMA_URL = os.getenv("LLAMA_URL", "http://localhost:8080")
LLAMA_FAILBACK_URL = os.getenv("LLAMA_FAILBACK_URL", "http://localhost:8080")
LLAMA_MAX_WORDS= int(os.getenv("LLAMA_MAX_WORDS","1000"))
LLAMA_TOP_P= float(os.getenv("LLAMA_TOP_P","0.6"))
LLAMA_TEMPERATURE= float(os.getenv("LLAMA_TEMPERATURE","0.9"))
RHASSPY_URL = os.getenv("RHASSPY_HOST", "http://192.168.0.44:12101")
current_dir = os.path.dirname(__file__)
model_config = os.path.join(current_dir, 'llama-3.1-8B')
logger = logging.getLogger(__name__)

stop_signs_regex = r'(?<=[.!?:])|(?<=\.\.\.)'
is_sentence = r'.*[A-Za-z0-9].*'

stop_signs = [".", "!", "?", ":"]

json_template = {
    "model" : "llama3",
    "repeat_penalty": 1.7,
    "penalize_nl": True,
    "top_p": LLAMA_TOP_P,
    "temperature": LLAMA_TEMPERATURE,
    "cache_prompt": True,
}

post_text_headers = {'Content-Type': 'text/plain; charset=utf-8'}
latest_chats = []
system_prompt = "Tu es un chien-assistant femelle à trois tête s'appelant Cerbinou qui répond comme un enfant de manière brève, courte et concise aux questions posées. Évite les détails inutiles, les smileys et les didascalie. Le prompt est branché à un transcripteur textuelle : lorsque tu ne comprends pas une phrase, tu sais qu'elle a mal été transcrite donc que tu as mal entendu. Tu connais Kona, c'est une gentille voiture."

def get_prompt_response(prompt: str):
    global tokenizer
    user_prompt = build_user_prompt(prompt)
    request = json_template | {"messages" : user_prompt}
    try:
        response= requests.post(f"{LLAMA_URL}/v1/chat/completions", json=request, timeout=(2,30))
    except requests.exceptions.Timeout:
        response = requests.post(url=f"{LLAMA_FAILBACK_URL}/v1/chat/completions", json=request)
        logging.info("timeout from [%s] response from : %s", f"{LLAMA_URL}", LLAMA_FAILBACK_URL)
    except requests.exceptions.ConnectionError:
        response = requests.post(url=f"{LLAMA_FAILBACK_URL}/v1/chat/completions", json=request)
        logging.info("connection refuse to[%s] response from : %s",LLAMA_URL, LLAMA_FAILBACK_URL)
    telegram.send_message(text=prompt, quote=True)       
    process_response(response)


def build_user_prompt(prompt: str):
    global system_prompt
    current_state = f"{system_prompt}\n{get_time_speech()}\n{task.get_weather()}" 
    chat = [
        {
            "role": "system",
            "content": current_state   
        }
    ]
    chat += latest_chats
    
    chat += [{
        "role": "user",
        "content": prompt
    }]
    while len(str(chat).split()) > LLAMA_MAX_WORDS and len(chat) > 1:
        chat.remove(2)
    return chat
    
def add_answer_to_context(answer: str):
    global latest_chats
    latest_chats += [{
        "role": "assistant",
        "content": answer
    }]
    
def process_response(response: requests.Response):
    if response.status_code == 200:
        message = response.json()["choices"][0]["message"]["content"]
        flush_sentence(message)
        add_answer_to_context(message)
    

def process_stream_response(response: requests.Response):
    text_response = ""
    if response.status_code == 200:
        sentence = ""
        for line in response.iter_lines(decode_unicode=True):
            json_line = json.loads(line)
            if json_line["delta"]:
                sentence += json_line["delta"]
                text_response += sentence
                sentence = flush_sentence(sentence)
        logger.info("Response output %s", text_response)
        add_answer_to_context(text_response)

                
def flush_sentence(sentence: str):
    sentences_to_flush = re.split(stop_signs_regex, sentence)
    logger.info(f"phrase : {sentences_to_flush}") 
    if len(sentences_to_flush) > 1:
        for i in range(len(sentences_to_flush) - 1):
            if is_sentence.find(sentences_to_flush[i]) > 0:
                requests.post(f"{RHASSPY_URL}/api/text-to-speech", data=sentences_to_flush[i].encode("utf-8"), headers=post_text_headers)

    new_sentence = sentences_to_flush[-1]
    if any(symbol in new_sentence for symbol in stop_signs):
        if  is_sentence.find(new_sentence) > 0:
            requests.post(f"{RHASSPY_URL}/api/text-to-speech", data=new_sentence.encode("utf-8"), headers=post_text_headers)
        return ""
    else:
        return new_sentence


def get_time_speech(): 
    now = datetime.now()
    return now.strftime("On est le %A %d %B %Y et il est %H heures %M et %S secondes")


