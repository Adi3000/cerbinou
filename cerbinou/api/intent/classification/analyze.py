from intent.models import IntentRequest, IntentTypeRequest
import logging

logger = logging.getLogger(__name__)

def analyze_text(text: str):
    cleared_text = ''.join(filter(str.isalnum, text))
    logger.info("String cleared was <%s>", cleared_text)
    if len(cleared_text) == 0:
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