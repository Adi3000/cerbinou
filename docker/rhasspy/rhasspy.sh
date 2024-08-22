#!/bin/bash
docker run --name rhasspy -p 12101:12101 -p 12183:12183 -v ./config:/root/.config/rhasspy --network host rhasspy/rhasspy -p fr
