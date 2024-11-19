from datetime import datetime
import httpx
import asyncio
import logging  
import re
import json
import os
from audit import telegram
from intent.handle.weather import task

LLAMA_URL = os.getenv("LLAMA_URL", "http://localhost:8080")
LLAMA_FAILBACK_URL = os.getenv("LLAMA_FAILBACK_URL", "http://localhost:8080")
LLAMA_MAX_WORDS= int(os.getenv("LLAMA_MAX_WORDS","1500"))
LLAMA_TOP_P= float(os.getenv("LLAMA_TOP_P","0.6"))
LLAMA_TEMPERATURE= float(os.getenv("LLAMA_TEMPERATURE","0.9"))
MODEL_TYPE= os.getenv("MODEL_TYPE", "gemma")
RHASSPY_URL = os.getenv("RHASSPY_HOST", "http://192.168.0.44:12101")
logger = logging.getLogger(__name__)

stop_signs_regex = r'([.!?:\u2026\n]{1,3})'
is_sentence = r'.*[A-Za-z0-9].*'

stream_cleaner = r'^data:\s*(\{.*\})\n*'


stop_signs = [".", "!", "?", ":", "\n"]

json_template = {
    "model" : MODEL_TYPE,
    "repeat_penalty": 1.7,
    "penalize_nl": True,
    "top_p": LLAMA_TOP_P,
    "temperature": LLAMA_TEMPERATURE,
    "cache_prompt": True,
    "stream": True
}

post_text_headers = {'Content-Type': 'text/plain; charset=utf-8'}
latest_chats = []
system_prompt = "Tu es un chien-assistant femelle à trois tête s'appelant Cerbinou qui répond comme un enfant de manière brève, courte et concise aux questions posées. Évite les détails inutiles, les smileys et les didascalie. Le prompt est branché à un transcripteur textuelle : lorsque tu ne comprends pas une phrase, tu sais qu'elle a mal été transcrite donc que tu as mal entendu. Tu connais Kona, c'est une gentille voiture électrique."

tts_tasks=[]
def get_prompt_response(prompt: str):
    global tokenizer
    global tts_tasks
    user_prompt = build_user_prompt(prompt)
    request = json_template | {"messages" : user_prompt}
    response = None
    

    telegram.send_message(text=prompt, quote=True)
    try:
        if json_template["stream"]:
            asyncio.run(process_stream_response(LLAMA_URL, request))
        else:
            response= httpx.post(f"{LLAMA_URL}/v1/chat/completions", json=request, timeout=(2,300))
    except (httpx.TimeoutException, httpx.ReadError) as err:
        logging.info("timeout from [%s] response from : %s\n%s", f"{LLAMA_URL}", LLAMA_FAILBACK_URL, err)
        if json_template["stream"]:
            asyncio.run(process_stream_response(LLAMA_FAILBACK_URL, request))
        else:
            response = httpx.post(url=f"{LLAMA_FAILBACK_URL}/v1/chat/completions", json=request, timeout=(2,300))
    
    if not json_template["stream"]:
        process= process_response(response)
        process_task = asyncio.create_task(process)
        asyncio.shield(process_task)
        tts_tasks += [process_task]


async def process_stream_response(url, request):
    async with httpx.AsyncClient() as client:
        async with client.stream("POST", f"{url}/v1/chat/completions", json=request, timeout=(2,300)) as response:
            text_response = ""
            sentence = ""
            async for chunk in response.aiter_bytes():
                str_chunk = chunk.decode("utf-8")
                cleared_chunk_match = re.search(stream_cleaner, str_chunk)
                if cleared_chunk_match:
                    json_chunk = json.loads(cleared_chunk_match.group(1))
                    if json_chunk["choices"] and json_chunk["choices"][0]["delta"] and json_chunk["choices"][0]["delta"]["content"]:
                        sentence += json_chunk["choices"][0]["delta"]["content"]
                        text_response += json_chunk["choices"][0]["delta"]["content"]
                        sentence = flush_sentence(sentence)
            if sentence.strip():
                flush_sentence(sentence)
            text_response = re.sub(r"\n+","\n", text_response)
            logger.info("Response output %s", text_response)
            add_answer_to_context(text_response)

def build_user_prompt(prompt: str):
    global system_prompt
    current_state = f"{system_prompt}\n{get_time_speech()}\n{task.get_weather()}" 
    chat = [
        {
            "role": "system",
            "content": current_state   
        }
    ]
    if MODEL_TYPE == "gemma":
        chat = [
            {
                "role": "user",
                "content": current_state
            }, {
                "role": "assistant",
                "content": "Salut, moi c'est Cerbinou ! Je suis content d'être là prêt à raconter des histoire ou aider la famille."
            },
        ]
    chat += latest_chats
    
    chat += [{
        "role": "user",
        "content": prompt
    }]
    while len(str(chat).split()) > LLAMA_MAX_WORDS and len(chat) > 1:
        if MODEL_TYPE == "gemma":
            del chat[2]
            del chat[2]
        else:
            del chat[1]
    return chat
    
def add_answer_to_context(answer: str):
    global latest_chats
    latest_chats += [{
        "role": "assistant",
        "content": answer
    }]
    
async def process_response(response: httpx.Response):
    if response.status_code == 200:
        message = response.json()["choices"][0]["message"]["content"]
        flush_sentence(message)
        add_answer_to_context(message)
    

def flush_sentence(sentence: str):
    sentences_to_flush = re.split(stop_signs_regex, sentence)
    if len(sentences_to_flush) > 1:
        for i in range(len(sentences_to_flush) - 1):
            stripped_sentence = sentences_to_flush[i].strip()
            if i+1 < len(sentences_to_flush) and re.match(stop_signs_regex,sentences_to_flush[i+1].strip()):
                stripped_sentence = sentences_to_flush[i] + sentences_to_flush[i+1]
                stripped_sentence = stripped_sentence.strip()
                i = i + 1
            if re.search(is_sentence, stripped_sentence):
                logger.info(f"phrase to flush (part) : {stripped_sentence}") 
                httpx.post(f"{RHASSPY_URL}/api/text-to-speech", data=stripped_sentence.encode("utf-8"), headers=post_text_headers)

    new_sentence = sentences_to_flush[-1].strip()
    if any(symbol in new_sentence for symbol in stop_signs):
        if  re.search(is_sentence,new_sentence):
            logger.info(f"phrase to flush (last) : {stripped_sentence}") 
            httpx.post(f"{RHASSPY_URL}/api/text-to-speech", data=new_sentence.encode("utf-8"), headers=post_text_headers)
        return ""
    else:
        return new_sentence

async def wait_tts_task():
    global tts_tasks
    for task in tts_tasks:
        await task
    

def get_time_speech(): 
    now = datetime.now()
    return now.strftime("On est le %A %d %B %Y et il est %H heures %M et %S secondes")


