#!/bin/bash

if [ -n "$1" ]; then
    cd /var/www/api.joemcalister.com/html/ami/speech/cerevoice/
    echo "$1" >> toRender.txt
    cd sdk
    timestamp=$(shuf -i 1-10000000000000000000 -n 1)
    ./txt2wav config/cerevoice_heather_4.0.0_48k.voice config/license.lic ../toRender.txt ../outputs/server_render/"$timestamp"_original.wav
    #&> /dev/null
    sox ../outputs/server_render/"$timestamp"_original.wav ../outputs/server_render/"$timestamp".wav echo .5 .5 30 .5
    rm ../outputs/server_render/"$timestamp"_original.wav
    cd ../
    rm toRender.txt
    echo "https://api.joemcalister.com/ami/speech/cerevoice/outputs/server_render/$timestamp.wav"
    #echo "something is going wrong"
else
    echo "You need to provide the text to be synthesised as an argument"
fi
