# 
#docker build --build-arg http_proxy=http://$(docker inspect --format '{{ .NetworkSettings.IPAddress }}' squid):3128 --tag=registry.guiraudet.com:5000/rpi-snap . && docker push registry.guiraudet.com:5000/rpi-snap


FROM registry.guiraudet.com:5000/rpi-base

RUN apt-get update &&\
    apt-get install -y python3-pip python3-dev wget &&\
    pip3 install --upgrade pip



# Install Adafruit-Motor-HAT-Python-Library and Rpi.gpio
RUN apt-get update &&\
    apt-get install -y python-dev git &&\
    echo
RUN cd /tmp &&\
    git clone https://github.com/adafruit/Adafruit-Motor-HAT-Python-Library.git  &&\
    cd Adafruit-Motor-HAT-Python-Library &&\
    python3 setup.py install &&\
    python  setup.py install &&\
    pip3 install rpi.gpio &&\
    pip install rpi.gpio &&\
    echo -e "\nCleaning-up.." &&\
    rm -fr /tmp/Adafruit-Motor-HAT-Python-Library 

# Install picamera and Pillow (PIL)
RUN apt-get install -y python-picamera python3-picamera libjpeg-dev &&\
    pip3 install Pillow
RUN pip3 install matplotlib

## OpenCV
#RUN apt-get install -y python-opencv python-flask v4l-utils v4l-conf

RUN pip3 install Flask

RUN mkdir -p /home/snap && cd /home/snap &&\
    git clone https://github.com/jmoenig/Snap--Build-Your-Own-Blocks.git static  &&\
    git clone https://github.com/pbrown66/snap-RPi.git &&\
    wget https://raw.githubusercontent.com/pbrown66/snap-RPi/master/RPiGPIO.xml -O static/libraries/RPiGPIO.xml

WORKDIR /home/snap
 
ADD server/ /home/snap/
ADD static/      /home/snap/static/

CMD python3 /home/snap/snap-server.py


