FROM registry.guiraudet.com:5000/rpi-base
MAINTAINER Jean-Marc Guiraudet <jguiraudet@gmail.com>



# Install webserver and deamon supervisor:
RUN DEBIAN_FRONTEND=noninteractive apt-get update &&\
    DEBIAN_FRONTEND=noninteractive apt-get -y install \
        nginx 


#### Copy files
COPY etc     /etc
COPY var     /var

# Expose server port
#EXPOSE 34448

# Set the application working directory
WORKDIR /root


ENV TERM=xterm

CMD ["/usr/sbin/nginx"]

## Logs do not need to be preserved when exporting
#VOLUME ["/var/log"]

