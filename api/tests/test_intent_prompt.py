import pytest
import httpx
from intent.handle.prompt import intent_prompt



def test_config():
    assert intent_prompt.json_template["model"] == "gemma"
    

def test_flush_sentence_with_one_sentence(mocker):
    mock_tts_post = mocker.patch("httpx.post")
    mock_tts_post.return_value = httpx.Response(200)
    
    last_sentence = intent_prompt.flush_sentence("Bonjour, c'est moi.")
    assert not last_sentence
    
    mock_tts_post.assert_called_once()
    _, kwargs = mock_tts_post.call_args
    assert kwargs["data"] == b"Bonjour, c'est moi."

def test_flush_sentence_with_twice_sentence(mocker):
    mock_tts_post = mocker.patch("httpx.post")
    mock_tts_post.return_value = httpx.Response(200)
    
    last_sentence = intent_prompt.flush_sentence("Bonjour, c'est moi. Comment ca va ?")
    
    assert not last_sentence
    all_calls = mock_tts_post.call_args_list
    
    _, kwargs1 = all_calls[0]
    assert kwargs1["data"] == b"Bonjour, c'est moi."
    _, kwargs2 = all_calls[1]
    assert kwargs2["data"] == b"Comment ca va ?"

def test_flush_sentence_with_multiple_punctuation(mocker):
    mock_tts_post = mocker.patch("httpx.post")
    mock_tts_post.return_value = httpx.Response(200)
    
    last_sentence = intent_prompt.flush_sentence("Je n'ai pas compris \"une petite souris... Elle a un chapeau rouge !!\" et je ne peux donc continuer l'histoire.")
    
    assert not last_sentence
    all_calls = mock_tts_post.call_args_list
    
    _, kwargs1 = all_calls[0]
    assert kwargs1["data"] == b"Je n'ai pas compris \"une petite souris..."
    _, kwargs2 = all_calls[1]
    assert kwargs2["data"] == b"Elle a un chapeau rouge !"
    _, kwargs2 = all_calls[2]
    assert kwargs2["data"] == b"\" et je ne peux donc continuer l'histoire."
    
   
def test_flush_sentence_with_twice_sentence_with_horizontal_ellipsis(mocker):
    mock_tts_post = mocker.patch("httpx.post")
    mock_tts_post.return_value = httpx.Response(200)
    
    last_sentence = intent_prompt.flush_sentence("Le voyage fut long mais ils ne baissaient pas les yeux sur leur objectif final: la renaissance d'un monde perdu. L'espoir, tel qu'il etait avant le chaos svelte et cruel qui a dechire l'ame du ciel nocturne\u2026")
    
    assert not last_sentence
    all_calls = mock_tts_post.call_args_list
    
    _, kwargs1 = all_calls[0]
    assert kwargs1["data"] == b"Le voyage fut long mais ils ne baissaient pas les yeux sur leur objectif final:"
    _, kwargs2 = all_calls[1]
    assert kwargs2["data"] == b"la renaissance d'un monde perdu."
    _, kwargs2 = all_calls[2]
    assert kwargs2["data"] == b"L'espoir, tel qu'il etait avant le chaos svelte et cruel qui a dechire l'ame du ciel nocturne\xe2\x80\xa6"

@pytest.mark.asyncio
async def test_stream_response():
    user_prompt = intent_prompt.build_user_prompt("Raconte moi une histoire de Minfilia et Tataru de Final Fantasy 14")
    request = intent_prompt.json_template | {"messages" : user_prompt}
    
    async with httpx.AsyncClient() as client:
        async with client.stream("POST", f"{intent_prompt.LLAMA_URL}/v1/chat/completions", json=request) as response:
            assert response.status_code == 200  # Check the status code
            # Stream the response in chunks
            async for chunk in response.aiter_bytes():
                # Process each chunk
                assert chunk  # Ensure the chunk is not empty
                print(chunk.decode("utf-8"))  # Print the chunk (if text)
                
@pytest.mark.asyncio
async def test_process_stream_response(mocker):
    user_prompt = intent_prompt.build_user_prompt("Raconte moi une histoire de Minfilia et Tataru de Final Fantasy 14")
    request = intent_prompt.json_template | {"messages" : user_prompt}
    mock_tts_post = mocker.patch("httpx.post")

    await intent_prompt.process_stream_response(request)
    
    all_calls = mock_tts_post.call_args_list
    for i in range(len(all_calls)):
        _, kwargs = all_calls[i]
        print(" TTS for "+ kwargs["data"].decode())
                
if __name__ == '__main__':
    pytest.main()