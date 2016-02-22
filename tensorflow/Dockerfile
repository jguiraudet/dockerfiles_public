
FROM b.gcr.io/tensorflow/tensorflow-gpu
MAINTAINER Jean-Marc Guiraudet <jguiraudet@gmail.com>


WORKDIR /root

# Additional dev tools
RUN apt-get update &&\
    apt-get install -y git tig wget unzip &&\
    apt-get install -y python-opencv &&\
    ln -s /dev/null /dev/raw1394 &&\
    rm -rf /var/lib/apt/lists/*

#### Copy files
COPY root    /root
COPY etc     /etc
COPY var     /var

ENV PYTHONPATH /slow_scratch/python

# Run all processes through supervisord
#CMD ["/usr/bin/supervisord", "-c", "/etc/supervisord.conf"]
CMD SHELL=bash /usr/local/bin/jupyter notebook


# Logs do not need to be preserved when exporting
VOLUME ["/var/log"]

