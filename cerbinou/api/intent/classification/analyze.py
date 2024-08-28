from intent.models import IntentRequest, IntentTypeRequest
import re

def analyze_text(text: str):
    if re.sub(r"[a-zA-Z0-9]","", text):
        return IntentRequest(
            intent=IntentTypeRequest(name= None, confidence=1.0), 
            text=text,
            raw_text=text
        )
    return prompt_intent(text)

def prompt_intent(text: str):
    return IntentRequest(
        intent=IntentTypeRequest(name="Prompt", confidence=1.0), 
        text=text, 
        raw_text=text
    )