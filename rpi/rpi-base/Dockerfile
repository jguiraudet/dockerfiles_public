# 
#docker build --build-arg http_proxy=http://$(docker inspect --format '{{ .NetworkSettings.IPAddress }}' squid):3128 --tag=registry.guiraudet.com:5000/rpi-base . && docker push registry.guiraudet.com:5000/rpi-base


#FROM resin/rpi-raspbian
FROM jguiraudet/raspbian-for-x86_64:2017-03-02-raspbian-jessie-lite


# Create the user
RUN adduser \
    --system \
    --shell /bin/bash \
    --gecos 'User for managing of jupyter python server' \
    --group \
    --disabled-password \
    --home /home/jupyter \
    jupyter &&\
    echo "%jupyter         ALL = (ALL) NOPASSWD: ALL" >> /etc/sudoers  &&\
    adduser jupyter sudo  &&\
    adduser jupyter video &&\
    adduser jupyter i2c   &&\
    adduser jupyter gpio

WORKDIR /home/jupyter


