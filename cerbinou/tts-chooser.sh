#!/bin/bash

# Start the first child process in the background and capture its PID
echo "starting at $(date  +%s)" >&2
input_text="$@"
if [ -z "$input_text" ]; then
	read input_text
fi
sanitized_input_text=$(echo $input_text | sed -e s/\"/\'/g)
cloud_filename="/tmp/cloud_$(date +%s%N | md5sum | head -c 8).wav"
touch $cloud_filename
curl -s -X POST 'https://rhasspy.adi3000.com/api/text-to-speech' --data-raw "$sanitized_input_text" --connect-timeout 10 --output $cloud_filename 2> /dev/null &
cloud_pid=$!

# Start the second child process in the background and capture its PID
melotts_filename="/tmp/melo_$(date +%s%N | md5sum | head -c 8).wav"
touch $melotts_filename
curl -s -X POST 'http://192.168.0.21:8381/convert/tts' -H "Content-Type: application/json" --data-raw "{\"text\":\"$sanitized_input_text\",\"speed\":\"1.2\"}" --connect-timeout 10 --output $melotts_filename 2> /dev/null &
melo_pid=$!

# Loop until one of the processes completes
while true; do

    if test -s $melotts_filename && ! kill -0 $melo_pid 2>/dev/null; then
        echo "melo $melotts_filename" >&2
        kill $cloud_pid 2>/dev/null
        cat $melotts_filename
        break
    fi

    if test -s $cloud_filename && ! kill -0 $cloud_pid 2>/dev/null; then
        echo "Cloud $cloud_filename" >&2
        kill $melo_pid 2>/dev/null
        cat $cloud_filename
        break
    fi

    sleep 0.5

done
echo "ending at $(date  +%s)" >&2
rm -f $cloud_filename 2>/dev/null
rm -f $melotts_filename  2>/dev/null

exit 0
