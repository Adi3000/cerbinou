from fastapi import FastAPI, Request
from starlette.middleware.base import BaseHTTPMiddleware
import logging

logger = logging.getLogger(__name__)


# Middleware to log requests and responses
class LogRequestsMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Log the incoming request
        logging.info(f"Request: {request.method} {request.url}")
        body = await request.body()
        logging.debug(f"Request Body: {body.decode('utf-8')}")
        
        # Process the request and get the response
        response = await call_next(request)

        # Log the outgoing response
        logging.info(f"Response status: {response.status_code}")
        response_body = [section async for section in response.body_iterator]
        logging.debug(f"Response Body: {b''.join(response_body).decode('utf-8')}")
        
        # Rebuild the response object for the client
        response.body_iterator = iter(response_body)
        
        return response