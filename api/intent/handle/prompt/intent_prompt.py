from datetime import datetime
import httpx
import asyncio
import logging  
import re
import json
import os
from audit import telegram
from intent.handle.calendar import task as calendar
from intent.handle.weather import task as weather

LLAMA_URL = os.getenv("LLAMA_URL", "http://localhost:8080")
LLAMA_FAILBACK_URL = os.getenv("LLAMA_FAILBACK_URL", "http://localhost:8080")
LLAMA_MAX_WORDS= int(os.getenv("LLAMA_MAX_WORDS","3000"))
LLAMA_TOP_P= float(os.getenv("LLAMA_TOP_P","0.5"))
LLAMA_TEMPERATURE= float(os.getenv("LLAMA_TEMPERATURE","0.7"))
SENTENCE_MIN_FLUSH= int(os.getenv("SENTENCE_MIN_FLUSH","10"))
MODEL_TYPE= os.getenv("MODEL_TYPE", "gemma")
RHASSPY_URL = os.getenv("RHASSPY_HOST", "http://192.168.0.44:12101")
logger = logging.getLogger(__name__)

stop_signs_regex = r'([.!?:\u2026\n]{1,3})'
is_sentence = r'.*[A-Za-z0-9]+.*'

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
system_prompt = "Tu es un chien-robot-assistant plein d'imagination s'appelant Cerbinou qui repond comme un grand enfant. Tu es dans la maison de Papa, Maman et leur deux enfants William et Raphaël. Evite les smileys et les didascalie."

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
            response= httpx.post(f"{LLAMA_URL}/v1/chat/completions", json=request)
            response.raise_for_status()
    except (httpx.TimeoutException, httpx.ReadError) as err:
        logging.info("timeout from [%s] response from while Stream = %s: %s\n%s", f"{LLAMA_URL}", json_template["stream"], LLAMA_URL, err)
        raise  RuntimeError(f"Chat completion failed for prompt <{prompt}>") from err

    if not json_template["stream"]:
        process= process_response(response)
        process_task = asyncio.create_task(process)
        asyncio.shield(process_task)
        tts_tasks += [process_task]


async def process_stream_response(url, request):
    timeout = httpx.Timeout(connect=5.0, read=60.0, write=10.0, pool=5.0)
    async with httpx.AsyncClient(timeout=timeout) as client:
        async with client.stream("POST", f"{url}/v1/chat/completions", json=request) as response:
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
                    elif "choices" not in json_chunk or json_chunk["choices"][0]["finish_reason"] == "stop":
                        logging.info("End of streaming (remaining sentence: <%s>)", sentence)
                        break
            if sentence.strip():
                flush_sentence(sentence)
            text_response = re.sub(r"\n+","\n", text_response)
            logger.info("Response output %s", text_response)
            add_answer_to_context(text_response)

def build_user_prompt(prompt: str):
    global system_prompt
    current_state = f"{system_prompt}\n{calendar.get_time_speech()}\n{calendar.get_next_tasks()}\n{weather.get_weather()}" 
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
    chat_lenght =  len(str(chat).split()) 
    logging.info(f" Chat size is %d / %d words", chat_lenght, LLAMA_MAX_WORDS)
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

def strip_stop_signs(sentence: str):
    stripped = sentence.replace("...", "\u2026")
    return stripped.strip()

def sanitize(sentence: str):
    sanitized = sentence.replace("\u2026", "...")
    return sanitized

def flush_sentence(sentence: str):
    if len(sentence) > SENTENCE_MIN_FLUSH:
        return force_flush_sentence(sentence)
    else:
        return sentence

def force_flush_sentence(sentence: str):
    sentences_to_flush = re.split(stop_signs_regex, strip_stop_signs(sentence))
    if len(sentences_to_flush) > 1:
        i = 0
        while i < len(sentences_to_flush) - 1:
            stripped_sentence = sentences_to_flush[i].strip()
            if i+1 < len(sentences_to_flush) and re.match(stop_signs_regex,sentences_to_flush[i+1].strip()):
                stripped_sentence = sentences_to_flush[i] + sentences_to_flush[i+1]
                stripped_sentence = strip_stop_signs(stripped_sentence)
                i = i + 1
                print(f"Sentence <{stripped_sentence}>")
            if re.search(is_sentence, stripped_sentence):
                logger.info(f"phrase to flush (part) : {stripped_sentence}") 
                try:                
                    httpx.post(f"{RHASSPY_URL}/api/text-to-speech", data=stripped_sentence.encode("utf-8"), headers=post_text_headers)
                except Exception as e:
                    logging.info(f"Did not had time to finish sending [{stripped_sentence}] due to <{e}>")
            i = i + 1


    new_sentence = sentences_to_flush[-1].strip()
    if any(symbol in new_sentence for symbol in stop_signs):
        if  re.search(is_sentence,new_sentence):
            logger.info(f"phrase to flush (last) : {stripped_sentence}") 
            tts_response = httpx.post(f"{RHASSPY_URL}/api/text-to-speech", data=new_sentence.encode("utf-8"), headers=post_text_headers)
            logger.info(" Processed with %s", tts_response.status_code)
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


