# 
#docker build --build-arg http_proxy=http://$(docker inspect --format '{{ .NetworkSettings.IPAddress }}' squid):3128 --tag=registry.guiraudet.com:5000/rpi-jupyter . && docker push registry.guiraudet.com:5000/rpi-jupyter


FROM registry.guiraudet.com:5000/rpi-base

RUN apt-get update &&\
    apt-get install -y python3-pip python3-dev wget
RUN pip3 install --upgrade pip
#RUN pip install html5lib==1.0b8
#RUN pip install widgetsnbextension
RUN pip3 install jupyter
RUN pip3 install jupyterlab
RUN jupyter serverextension enable --py jupyterlab --sys-prefix


#apt-get install -y build-essential git cmake pkg-config libjpeg-dev libtiff5-dev libjasper-dev libpng12-dev libavcodec-dev libavformat-dev libswscale-dev libv4l-dev libxvidcore-dev libx264-dev  libatlas-base-dev gfortran 
#sudo ln /dev/null /dev/raw1394
#apt-get install -y python-opencv

#sudo apt-get install -y python-picamera python3-picamera
# Create a local docker network to be able to resolve container IP address by their names
# 196  docker network create robot
#  199  docker run -d -p 80:8888 --privileged --volume /dev:/dev --restart=always --name jupyter --net robot jguiraudet/rpi-jupyter 

# Install RPI interface library
RUN apt-get install -y python-picamera python3-picamera

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

# OpenCV
RUN apt-get install -y python-opencv python-flask v4l-utils v4l-conf
RUN pip3 install flask

WORKDIR /home/jupyter
USER jupyter

 
CMD SHELL=/bin/bash jupyter notebook  --NotebookApp.token="" --NotebookApp.base_url="/jupyter/" --ip=0.0.0.0 --no-browser

