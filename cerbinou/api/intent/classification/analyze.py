from intent.models import IntentRequest, IntentTypeRequest

def analyze_text(text: str):
    return prompt_intent(text)


def prompt_intent(text: str):
    return IntentRequest(
        intent=IntentTypeRequest(name="Prompt", confidence=1.0), 
        text=text, 
        raw_text=text
    )