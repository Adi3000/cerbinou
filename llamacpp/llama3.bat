set LLAMA_HOME=G:\Utils\llama
set GGUF_MODELS=G:\Utils\llama\models\gemma-2-2b-it-Q8_0.gguf
REM set GGUF_MODELS=G:\Utils\llama\models\Ministral-8B-Instruct-2410-Q6_K.gguf
REM set GGUF_MODELS=G:\Utils\llama\models\Llama-3.2-3B-Instruct.Q8_0.gguf
set CERBINOU=E:\workspace\cerbinou

%LLAMA_HOME%\llama-server.exe --host 0.0.0.0 --model %GGUF_MODELS% --ctx-size 2048 --gpu-layers 20 --threads 8 --top-p 0.6 --temp 0.9 --repeat-penalty 1.7 --penalize-nl 

