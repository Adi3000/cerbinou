from fastapi import FastAPI, Request
import uvicorn
from asr.speech_to_text import save_file
from utils import LogRequestsMiddleware
import logging
import os

CERBINOU_WORKER_PORT = int(os.getenv("CERBINOU_WORKER_PORT", "9977"))


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'  # Define the log format
)
    
logger = logging.getLogger(__name__)
worker_api = FastAPI()

@worker_api.post("/api/intent")
async def text_decode(request: Request):
    logging.info("Type : %s", request.headers.get('Content-Type'))
    # Read the binary data from the request body
    intent_text_data = await request.body()
    
    return save_file(audio_data)


if __name__ == "__main__":
    app.add_middleware(LogRequestsMiddleware)
    uvicorn.run("router:app", host="0.0.0.0", port=CERBINOU_WORKER_PORT, reload=False, log_level="info")
