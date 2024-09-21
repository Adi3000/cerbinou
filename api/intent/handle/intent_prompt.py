import requests
import logging  
import re
import json
import os
from audit import telegram

LLAMA_URL = os.getenv("LLAMA_URL", "http://localhost:8080")
LLAMA_FAILBACK_URL = os.getenv("LLAMA_FAILBACK_URL", "http://localhost:8080")
LLAMA_MAX_WORDS= int(os.getenv("LLAMA_MAX_WORDS","1000"))
RHASSPY_URL = os.getenv("RHASSPY_HOST", "http://localhost:12101")

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
        "user"
    ]

json_template = {
    "stop": [
        "</s>",
        "<|end|>",
        "<|eot_id|>",
        "<|end_of_text|>",
        "<|im_end|>",
        "<|EOT|>",
        "<|END_OF_TURN_TOKEN|>",
        "<|end_of_turn|>",
        "<|endoftext|>",
        "cerbinou",
        "user"
    ],
    "repeat_penalty": 1.7,
    "penalize_nl": True,
    "top_p": 0.6,
    "temperature": 0.9,
    "cache_prompt": True,
}

prompt_context =  "Bonjour, es-tu disponible ?<|eot_id|><|start_header_id|>cerbinou<|end_header_id|>\n\nOui bien sûr, que veux tu savoir ?<|eot_id|><|start_header_id|>user<|end_header_id|>\n\n"
post_text_headers = {'Content-Type': 'text/plain; charset=utf-8'}

def get_prompt_response(prompt: str):
    global prompt_context
    add_prompt_to_context(prompt)
    try:
        response= requests.post(f"{LLAMA_URL}/completion", json= {"prompt": purge_context(prompt_context)}, timeout=(2,30), stream=True)
    except requests.exceptions.Timeout:
        response = requests.post(url=f"{LLAMA_FAILBACK_URL}/completion", json= {"prompt": purge_context(prompt_context)}, )
        logging.info("timeout from [%s] response from : %s", f"{LLAMA_URL}", LLAMA_FAILBACK_URL)
    except requests.exceptions.ConnectionError:
        response = requests.post(url=f"{LLAMA_FAILBACK_URL}/completion", json= {"prompt": purge_context(prompt_context)})
        logging.info("connection refuse to[%s] response from : %s",LLAMA_URL, LLAMA_FAILBACK_URL)
        
    logger.info("Response output %s", response.json())
    process_stream_reponse(response)
    telegram.send_message(text=prompt, quote=True)


def add_prompt_to_context(prompt: str):
    global prompt_context
    prompt_context += f"{prompt}<|eot_id|><|start_header_id|>cerbinou<|end_header_id|>\n\n"

def add_answer_to_context(answer: str):
    global prompt_context
    prompt_context += f"{answer}<|eot_id|><|start_header_id|>user<|end_header_id|>\n\n"
    
def check_nb_token(context: str):
    sanitized_text = context.replace("<|eot_id|><|start_header_id|>cerbinou<|end_header_id|>", "").replace("<|eot_id|><|start_header_id|>user<|end_header_id|>", "")
    return len(sanitized_text.split()) <= LLAMA_MAX_WORDS

def purge_context(context: str):
    if check_nb_token(context):
        return context
    else:
        context_parts = context("<|eot_id|><|start_header_id|>user<|end_header_id|>\n\n", 1)
        if(len(context_parts) > 1):
            return purge_context(context_parts[1])
        else:
            return context


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
        add_answer_to_context(text_response)

                
def flush_sentence(sentence: str):
    sentences_to_flush = re.split(stop_signs_regex, sentence)
    logger.info(f"phrase : {sentence}") 
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
