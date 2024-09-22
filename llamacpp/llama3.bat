set LLAMA_HOME=G:\Utils\llama
set GGUF_MODELS=G:\Utils\llama\models\Meta-Llama-3.1-8B-Instruct-Q6_K.gguf
set CERBINOU=E:\workspace\cerbinou

%LLAMA_HOME%\llama-server.exe --host 0.0.0.0 --model %GGUF_MODELS% --ctx-size 2048 --gpu-layers 20 --threads 8 --top-p 0.6 --temp 0.9 --repeat-penalty 1.7 --penalize-nl --prompt-cache %LLAMA_HOME%\prompt-cache.bin --conversation

