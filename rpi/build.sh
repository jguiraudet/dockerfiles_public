#!/bin/bash

set -e

PROXY=http://$(docker inspect --format '{{ .NetworkSettings.IPAddress }}' squid):3128

#for F in rpi-base rpi-jupyter rpi-reverse-proxy
for F in rpi-base rpi-reverse-proxy rpi-jupyter 
do
    echo
    echo "Building $F"
    docker build --build-arg http_proxy=$PROXY --tag=registry.guiraudet.com:5000/$F $F 
    docker push registry.guiraudet.com:5000/$F
done
