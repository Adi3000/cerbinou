FROM nvcr.io/nvidia/cuda:11.8.0-cudnn8-devel-ubuntu22.04

RUN apt-get update \ 
    && apt-get install -y git git-lfs curl python3 python3-pip ffmpeg libmagic1 \
    && curl -s https://packagecloud.io/install/repositories/github/git-lfs/script.deb.sh | bash \
    && git lfs install \
    && rm cuda-keyring_1.0-1_all.deb \
    && ln -s /usr/bin/python3 /usr/bin/python \
    && rm -rf /var/lib/apt/lists/* \
    && mkdir app

RUN pip3 install --no-cache-dir torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118 \
 && pip3 install --no-cache-dir 'nvidia-cudnn-cu11<9.0.0' --index-url https://download.pytorch.org/whl/nightly \
 && pip3 install git+https://github.com/myshell-ai/MeloTTS.git@main \
 && pip3 install git+https://github.com/myshell-ai/OpenVoice.git@main \
 && pip3 install --no-cache-dir gradio==3.48.0

WORKDIR /app

RUN git clone https://huggingface.co/myshell-ai/OpenVoiceV2 \
 && git clone https://github.com/ground-creative/openvoice-api-python.git \
 && cd openvoice-api-python && pip3 install --no-cache-dir -r requirements.txt \
 && python -m unidic download