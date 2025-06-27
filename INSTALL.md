## How to run dockers

```
docker run --name=whisper --gpus all -p 9000:9000 -e ASR_MODEL=base -e ASR_ENGINE=openai_whisper onerahmet/openai-whisper-asr-webservice:latest-gpu
```

```
docker run -p 9000:9000 -e ASR_MODEL=base -e ASR_ENGINE=openai_whisper onerahmet/openai-whisper-asr-webservice:latest
```

## Rhasspy dependencies to adjust 

```
git clone git@github.com:Adi3000/rhasspy.git
git submodule update --recursive --remote
 ./configure  RHASSPY_LANGUAGE=fr --disable-speech-to-text --disable-precise --disable-snowboy --disable-nanotts --disable-wavenet --disable-larynx --enable-in-place
make
sudo make install
```

Use python 3.7.7 environment
Override requirements from rhasspy within rhasspy and rhasspy-tts-cli-hermes

```
Jinja2<3.1.0
```


## PiDog

To avoid running pidog with sudo to play sound just copy 
```
cp /etc/asound.conf /home/pi/.asound
```
into the `pi` user
Then `sudo killall pulseaudio`
then try again a `python3 pidog/examples/1_wake_up.py`

