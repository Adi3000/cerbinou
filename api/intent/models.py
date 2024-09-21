from pydantic import BaseModel
from typing import Optional
    
class Speech(BaseModel):
    text: str

class IntentResponse(BaseModel):
    speech: Speech
    
class IntentTypeRequest(BaseModel):
    name: Optional[str]
    confidence: float
    
class IntentRequest(BaseModel):
    intent: IntentTypeRequest
    text: str
    raw_text: str
    
class IntentType(BaseModel):
    intentName: str
    confidenceScore: float
    
    
class NoIntent(BaseModel):
    input: str
    siteId: str
    id: str
    sessionId: str
    
class ParsedIntent(NoIntent):
    intent: IntentType
    slots: list[str] = []

class IntentMQTT(ParsedIntent):
    asrTokens: list[str] = []
    asrConfidence: Optional[str] = None
    customData: Optional[str] = None
    rawInput: str
    wakewordId: Optional[str] = None
    lang: Optional[str] = None
    