# Ubuntu developer image
FROM ubuntu:14.04.3



# Install docker. See: http://docs.docker.com/engine/installation/ubuntulinux/
RUN apt-key adv --keyserver hkp://pgp.mit.edu:80 --recv-keys 58118E89F3A912897C070ADBF76221572C52609D &&\
    bash -c 'echo "deb https://apt.dockerproject.org/repo ubuntu-$(lsb_release -sc) main" > /etc/apt/sources.list.d/docker.list' &&\
    apt-get install -qqy  apt-transport-https &&\
    apt-get update -qq &&\
    apt-get install -qqy docker-engine &&\
    rm -rf /var/lib/apt/lists/*
    
# Add unsecure local registry
RUN  echo 'DOCKER_OPTS="$DOCKER_OPTS --insecure-registry myregistry:5000"' >> /etc/default/docker
