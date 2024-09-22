from transformers import AutoTokenizer
from datetime import datetime
import requests
import logging  
import re
import json
import os
from audit import telegram

LLAMA_URL = os.getenv("LLAMA_URL", "http://localhost:8080")
LLAMA_FAILBACK_URL = os.getenv("LLAMA_FAILBACK_URL", "http://localhost:8080")
LLAMA_MAX_WORDS= int(os.getenv("LLAMA_MAX_WORDS","1000"))
LLAMA_TOP_P= float(os.getenv("LLAMA_TOP_P","0.6"))
LLAMA_TEMPERATURE= float(os.getenv("LLAMA_TEMPERATURE","0.9"))
RHASSPY_URL = os.getenv("RHASSPY_HOST", "http://192.168.0.44:12101")

logger = logging.getLogger(__name__)

stop_signs_regex = r'(?<=[.!?:])|(?<=\.\.\.)'
stop_signs = [".", "!", "?", ":"]
stop_list = [
        "</s>",
        "<|end|>",
        "<|eot_id|>",
        "<|end_of_text|>",
        "<|im_end|>",
        "<|EOT|>",
        "<|END_OF_TURN_TOKEN|>",
        "<|end_of_turn|>",
        "<|endoftext|>",
        "assistant",
        "user",
        "system"
    ]

json_template = {
    "repeat_penalty": 1.7,
    "penalize_nl": True,
    "top_p": LLAMA_TOP_P,
    "temperature": LLAMA_TEMPERATURE,
    "cache_prompt": True,
}

prompt_context =  "Bonjour, es-tu disponible ?<|eot_id|><|start_header_id|>cerbinou<|end_header_id|>\n\nOui bien sûr, que veux tu savoir ?<|eot_id|><|start_header_id|>user<|end_header_id|>\n\n"
post_text_headers = {'Content-Type': 'text/plain; charset=utf-8'}
latest_chats = []
system_prompt = "Tu es un chien-assistant femelle à trois tête s'appelant Cerbinou qui répond comme un enfant de manière brève, courte et concise aux questions posées. Évite les détails inutiles, les smileys et les didascalie. Le prompt est branché à un transcripteur textuelle : lorsque tu ne comprends pas une phrase, tu sais qu'elle a mal été transcrite donc que tu as mal entendu. Tu connais Kona, c'est une gentille voiture."
def get_prompt_response(prompt: str):
    tokenizer = AutoTokenizer.from_pretrained("unsloth/Meta-Llama-3.1-8B-Instruct-bnb-4bit")
    user_prompt = build_user_prompt(prompt)
    prompt_request = tokenizer.apply_chat_template(tokenize=False,max_length=LLAMA_MAX_WORDS, conversation=user_prompt,  add_generation_prompt=True)
    try:
        response= requests.post(f"{LLAMA_URL}/completion", json= {"prompt": prompt_request}, timeout=(2,30), stream=True)
    except requests.exceptions.Timeout:
        response = requests.post(url=f"{LLAMA_FAILBACK_URL}/completion", json= {"prompt": prompt_request}, stream=True)
        logging.info("timeout from [%s] response from : %s", f"{LLAMA_URL}", LLAMA_FAILBACK_URL)
    except requests.exceptions.ConnectionError:
        response = requests.post(url=f"{LLAMA_FAILBACK_URL}/completion", json= {"prompt": prompt_request}, stream=True)
        logging.info("connection refuse to[%s] response from : %s",LLAMA_URL, LLAMA_FAILBACK_URL)
        
    process_stream_reponse(response)


def build_user_prompt(prompt: str):
    global prompt_context
    global system_prompt
    current_state = f"{get_time_speech()}. {system_prompt}" 
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
    telegram.send_message(text=answer, quote=True)


def process_stream_reponse(response: requests.Response):
    text_response = "";
    if response.status_code == 200:
        response.encoding = 'utf-8'
        sentence = "";
        for line in response.iter_lines(chunk_size=128):
            json_line = json.loads(line)
            if json_line["content"]:
                sentence += json_line["content"]
                text_response += sentence
                sentence = flush_sentence(sentence)
        logger.info("Response output %s", text_response)
        add_answer_to_context(text_response)

                
def flush_sentence(sentence: str):
    sentences_to_flush = re.split(stop_signs_regex, sentence)
    logger.debug(f"phrase : {sentence}") 
    if len(sentences_to_flush) > 1:
        for i in range(len(sentences_to_flush) - 1):
            if sentences_to_flush[i]:
                requests.post(f"{RHASSPY_URL}/api/text-to-speech", data=sentences_to_flush[i].encode("utf-8"), headers=post_text_headers)

    new_sentence = sentences_to_flush[-1]
    if any(symbol in new_sentence for symbol in stop_signs):
        if new_sentence:
            requests.post(f"{RHASSPY_URL}/api/text-to-speech", data=new_sentence.encode("utf-8"), headers=post_text_headers)
        return ""
    else:
        return new_sentence


def get_time_speech(): 
    now = datetime.now()
    return now.strftime("On est le %A %d %B %Y et il est %H heures %M et %S secondes")
