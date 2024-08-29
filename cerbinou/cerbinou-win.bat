@echo off
REM Step 1: Capture the WSL IP address using the given command
for /f %%i in ('wsl ip -4 -o addr show eth0 ^| tr -s " " ^| cut -d" " -f4 ^| cut -d/ -f1') do set WSL_IP=%%i

REM Step 2: Display the captured WSL IP address
echo The WSL IP address is: %WSL_IP%

netsh interface portproxy delete v4tov4 listenport=8381 listenaddress=0.0.0.0
netsh interface portproxy add v4tov4 listenport=8381 listenaddress=0.0.0.0 connectport=8381 connectaddress=%WSL_IP%
netsh advfirewall firewall add rule name="Allow Port 8381" dir=in action=allow protocol=TCP localport=8381

netsh interface portproxy delete v4tov4 listenport=9000 listenaddress=0.0.0.0
netsh interface portproxy add v4tov4 listenport=9000 listenaddress=0.0.0.0 connectport=9000 connectaddress=%WSL_IP%
netsh advfirewall firewall add rule name="Allow Port 9000" dir=in action=allow protocol=TCP localport=9000

wsl docker info
wsl docker compose -f /mnt/e/workspace/my-scripts/cerbinou/docker-compose.yaml up -d