@echo off
REM Step 1: Capture the WSL IP address using the given command
for /f %%i in ('wsl ip -4 -o addr show eth0 ^| tr -s " " ^| cut -d" " -f4 ^| cut -d/ -f1') do set WSL_IP=%%i

REM Step 2: Display the captured WSL IP address
echo The WSL IP address is: %WSL_IP%

wsl docker run --detach --name=melotts --env=DEFAULT_LANGUAGE=FR --env=DEFAULT_SPEAKER_ID=FR --env=DEFAULT_SPEED=1 -p 8381:8080 --restart=unless-stopped --volume /mnt/e/workspace/my-scripts/cerbinou/tts:/tts timhagel/melotts-api-server python app.py