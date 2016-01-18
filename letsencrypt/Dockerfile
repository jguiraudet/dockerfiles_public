# Create a SSL certificate with https://letsencrypt.org
#
# This container should have access to the network so that the letsencrypt
# client can exchange challenge with its server and authenticate this machine.

FROM jguiraudet/jekyll-dev

MAINTAINER Jean-Marc Guiraudet <jguiraudet@gmail.com>

VOLUME  /etc/letsencrypt
RUN	git clone https://github.com/letsencrypt/letsencrypt /opt/letsencrypt &&\
        cd /opt/letsencrypt &&\
        DEBIAN_FRONTEND=noninteractive ./letsencrypt-auto --help

RUN     DEBIAN_FRONTEND=noninteractive apt-get install -y apache2-utils

WORKDIR /opt/letsencrypt
EXPOSE  80 443
CMD    TERM=xterm ./letsencrypt-auto certonly --standalone --keep-until-expiring --agree-tos --text 

#or with default value like:
#CMD TERM=xterm ./letsencrypt-auto certonly --standalone --keep-until-expiring --agree-tos --text -m jguiraudet@gmail.com -d guiraudet.com -d www.guiraudet.com

