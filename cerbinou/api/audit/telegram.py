import requests
import html
import os
import asyncio

TELEGRAM_API_BOT= os.getenv("TELEGRAM_API_BOT","")
TELEGRAM_CHAT_ID= int(os.getenv("TELEGRAM_CHAT_ID","0"))


def send_message(text: str, quote: bool=False):
    if TELEGRAM_API_BOT and TELEGRAM_CHAT_ID != 0:
        message = text 
        if quote :
            message = "```\n" + text + "```"
        telegram_param = {
            "chat_id": TELEGRAM_CHAT_ID, 
            "text": message,
            "parse_mode": "markdown"
        } 
        requests.get(url = f"https://api.telegram.org/{TELEGRAM_API_BOT}/sendMessage", params= telegram_param)