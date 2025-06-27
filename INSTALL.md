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
conda install numpy==1.20.1 scipy==1.6.0 scikit-learn==0.23.2
./configure  RHASSPY_LANGUAGE=fr --disable-speech-to-text enable_precise=no enable_snowboy=no enable_nanotts=no enable_wavenet=no enable_larynx=no enable_pocketsphinx=no enable_raven=no enable_vosk=no --enable-in-place enable_virtualenv=no
make
make install
```

Use python 3.7.7 environment
Override requirements from rhasspy within rhasspy and rhasspy-tts-cli-hermes

```
Jinja2<3.1.0
```
and other like 
```
find -name "requirements*" -exec sed -i 's/black==19.10b0/black==22.10.0/g' "{}" \;
find -name "requirements*" -exec sed -i 's/coverage==5.0.4/coverage==6.2/g' "{}" \;
find -name "requirements*" -exec sed -i 's/pyyaml==5.4/pyyaml==6.0.2/g' "{}" \;
find -name "requirements*" -exec sed -i 's/pytest==5.4.1/pytest==6.2.5/g' "{}" \;
find -name "requirements*" -exec sed -i 's/flake8==4.0.1/flake8==4.0.1/g' "{}" \;
find -name "requirements*" -exec sed -i 's/flake8==3.7.9/flake8==4.0.1/g' "{}" \;
find -name "requirements*" -exec sed -i 's/pytest-cov==2.8.1/pytest==3.0.0/g' "{}" \;
find -name "requirements*" -exec sed -i 's/Jinja2==2.11.2/Jinja2==2.11.3/g' "{}" \;
find -name "requirements*" -exec sed -i 's/mypy==0.770/mypy==0.920/g' "{}" \;
find -name "requirements*" -exec sed -i 's/pvporcupine~=1.9.0/pvporcupine~=3.0.0/g' "{}" \;
find -name "requirements*" -exec sed -i 's/pytest==3.0.0/pytest==6.2.5/g' "{}" \;
find -name "requirements*" -exec sed -i 's/pylint==2.4.4/pylint==2.15.6/g' "{}" \;
find -name "requirements*" -exec sed -i 's/pylint==2.5.3/pylint==2.15.6/g' "{}" \;
find -name "requirements*" -exec sed -i 's/scipy==1.5.1/scipy==1.6.0/g' "{}" \;
find -name "requirements*" -exec sed -i 's/dataclasses-json==0.4.2/dataclasses-json==0.5.6/g' "{}" \;
find -name "requirements*" -exec sed -i 's/pyinstaller==3.6/pyinstaller==6.11.1/g' "{}" \;
find -name "requirements*" -exec sed -i 's/numpy>=1.19.0/numpy==1.20.1/g' "{}" \;
find -name "requirements*" -exec sed -i 's/scipy==1.5.1/scipy==1.6.0/g' "{}" \;
find -name "requirements*" -exec sed -i 's/quart==0.11.3/quart==0.20.0/g' "{}" \;
find -name "requirements*" -exec sed -i 's/hypercorn==0.10.1/hypercorn==0.17.3/g' "{}" \;
find -name "requirements*" -exec sed -i 's/quart==0.11.3/quart==0.14.1/g' "{}" \;
find -name "requirements*" -exec sed -i 's/quart-cors==0.3.0/quart-cors==0.4.0/g' "{}" \;
```

## PiDog

To avoid running pidog with sudo to play sound just copy 
```
cp /etc/asound.conf /home/pi/.asound
```
into the `pi` user
Then `sudo killall pulseaudio`
then try again a `python3 pidog/examples/1_wake_up.py`

