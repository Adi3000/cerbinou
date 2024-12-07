## How to run dockers

```
docker run --name=whisper --gpus all -p 9000:9000 -e ASR_MODEL=base -e ASR_ENGINE=openai_whisper onerahmet/openai-whisper-asr-webservice:latest-gpu
```

```
docker run -p 9000:9000 -e ASR_MODEL=base -e ASR_ENGINE=openai_whisper onerahmet/openai-whisper-asr-webservice:latest
```

## Rhasspy dependencies to adjust 

Use python 3.7.7 environment
Override requirements from rhasspy within rhasspy and rhasspy-tts-cli-hermes

```
Jinja2<3.1.0
```
