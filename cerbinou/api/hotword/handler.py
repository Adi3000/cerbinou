import websockets
import asyncio
import json
import logging

logger = logging.getLogger(__name__)

running = True

def wake():
    try:
        asyncio.run(wake_handler())
    except KeyboardInterrupt:
        logger.info("Received KeyboardInterrupt, stopping wake handler...")
        
async def wake_handler():
    
    global running
    uri = "ws://192.168.0.44:12101/api/mqtt"
    asrListenStartSubscription = {
        "type": "subscribe",
        "topic": "hermes/asr/startListening"
    }
    asrListenStopSubscription = {
        "type": "subscribe",
        "topic": "hermes/asr/stopListening"
    }
    toggleOffForAMessage = {
        "type": "subscribe",
        "topic": {"siteId": "adi-home", "reason": "talking"}
    }
    toggleOnListenFinishTalkingMessage = {
        "type": "subscribe",
        "topic": {"siteId": "adi-home", "reason": "finishedTalking"}
    }
    
    async with websockets.connect(uri) as websocket:
        
        await websocket.send(json.dumps(asrListenStartSubscription))
        await websocket.send(json.dumps(asrListenStopSubscription))
        while running:
            try:
                message = await websocket.recv()
                logger.info("Received message: %s",message)
            except websockets.ConnectionClosed:
                logger.warning("WebSocket connection closed")
                break
            except asyncio.CancelledError:
                logger.info("Listener for wake was cancelled")
                break
