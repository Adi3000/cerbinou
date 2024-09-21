#!/bin/bash

printf '{"speech":{"text":"il est %s heures %s et %s secondes"}}' $(date +%k) $(date +%M) $(date +%S)
