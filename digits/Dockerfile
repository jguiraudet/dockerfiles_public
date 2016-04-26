# Start with CUDA base image from nvidia. https://github.com/NVIDIA/nvidia-docker 
# Based on dockerfile from Kai Arulkumaran <design@kaixhin.com>

FROM cuda:7.5-cudnn3-devel
MAINTAINER Jean-Marc Guiraudet <jguiraudet@gmail.com>


WORKDIR /root

# Install git, bc and dependencies
RUN apt-get update  && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
	wget \
	git \
	doxygen \
	libgflags-dev \
	libgoogle-glog-dev \
	libopencv-dev \
    	libleveldb-dev \
	libsnappy-dev \
	liblmdb-dev \
	libhdf5-serial-dev \
	libprotobuf-dev \
	protobuf-compiler \
	libatlas-base-dev \
	gfortran \
	libboost-all-dev \
	cmake \
# Other DIGITS dependencies
	graphviz \
	gunicorn

# Install anaconda with python 2.7
RUN echo 'export PATH=/opt/conda/bin:$PATH' > /etc/profile.d/conda.sh && \
    wget http://repo.continuum.io/archive/Anaconda2-2.4.1-Linux-x86_64.sh && \
    /bin/bash ./Anaconda2-2.4.1-Linux-x86_64.sh -b -p /opt/conda && \
    rm ./Anaconda2-2.4.1-Linux-x86_64.sh
ENV PATH=/opt/conda/bin:$PATH


# Clone NVIDIA Caffe repo and move into it
# Use v0.14.0-rc.1 which is still compatible with cudnn v3
RUN git clone --branch caffe-0.14 http://github.com/NVIDIA/caffe.git &&\
    cd caffe &&\
    git checkout v0.14.0-rc.1 &&\
# Install python dependencies
  for req in $(cat python/requirements.txt); do echo Installing $req...; pip install $req; done
# Build
RUN mkdir caffe/build && cd caffe/build &&\
    cmake .. &&\
    make -j"$(nproc)" all &&\
    make -j"$(nproc)" pycaffe
# Set environment variable
ENV CAFFE_HOME /root/caffe

# Run Torch7 installation scripts
RUN curl -sk https://raw.githubusercontent.com/torch/ezinstall/master/install-deps | bash
RUN git clone https://github.com/torch/distro.git ~/torch --recursive
RUN cd ~/torch; ./install.sh

# Set ~/torch as working directory
WORKDIR /root/torch

# Export environment variables manually
ENV LUA_PATH='/root/.luarocks/share/lua/5.1/?.lua;/root/.luarocks/share/lua/5.1/?/init.lua;/root/torch/install/share/lua/5.1/?.lua;/root/torch/install/share/lua/5.1/?/init.lua;./?.lua;/root/torch/install/share/luajit-2.1.0-alpha/?.lua;/usr/local/share/lua/5.1/?.lua;/usr/local/share/lua/5.1/?/init.lua' \
  LUA_CPATH='/root/.luarocks/lib/lua/5.1/?.so;/root/torch/install/lib/lua/5.1/?.so;./?.so;/usr/local/lib/lua/5.1/?.so;/usr/local/lib/lua/5.1/loadall.so' \
  PATH=/root/torch/install/bin:$PATH \
  LD_LIBRARY_PATH=/root/torch/install/lib:$LD_LIBRARY_PATH \
  DYLD_LIBRARY_PATH=/root/torch/install/lib:$DYLD_LIBRARY_PATH

# Clone DIGITS and move into it
RUN cd /root && git clone http://github.com/NVIDIA/DIGITS.git digits && cd digits && \
# Install python dependencies
  for req in $(cat requirements.txt requirements_test.txt); do pip install $req; done


# install custom packages for torch
RUN luarocks install "http://raw.github.com/deepmind/torch-hdf5/master/hdf5-0-0.rockspec" &&\
    luarocks install "http://raw.github.com/Sravan2j/lua-pb/master/lua-pb-scm-0.rockspec" &&\
    luarocks install image  &&\
    luarocks install lightningmdb LMDB_INCDIR=/usr/include LMDB_LIBDIR=/usr/lib/x86_64-linux-gnu

# Install webserver and deamon supervisor:
RUN DEBIAN_FRONTEND=noninteractive apt-get -qqy install \
        nginx \
        supervisor && \
        mkdir /var/log/digits


# Install OpenCV from source
RUN apt-add-repository ppa:mc3man/trusty-media &&\
    apt-get update && \
    version="$(wget -q -O - http://sourceforge.net/projects/opencvlibrary/files/opencv-unix | egrep -m1 -o '\"[0-9](\.[0-9]+)+' | cut -c2-)" &&\
    echo "OpenCV last version available=$version"  &&\
    version=3.1.0  &&\
    echo "Installing OpenCV" $version  &&\
    mkdir /root/OpenCV  &&\
    cd /root/OpenCV  &&\
    echo "Removing any pre-installed ffmpeg and x264"  &&\
    sudo apt-get -qq remove ffmpeg x264 libx264-dev &&\
    echo "Installing Dependencies" &&\
    sudo apt-get -y install libopencv-dev build-essential checkinstall cmake pkg-config yasm libjpeg-dev libjasper-dev libavcodec-dev libavformat-dev libswscale-dev libdc1394-22-dev libxine-dev libgstreamer0.10-dev libgstreamer-plugins-base0.10-dev libv4l-dev python-dev python-numpy libtbb-dev libqt4-dev libgtk2.0-dev libfaac-dev libmp3lame-dev libopencore-amrnb-dev libopencore-amrwb-dev libtheora-dev libvorbis-dev libxvidcore-dev x264 v4l-utils ffmpeg cmake qt5-default checkinstall  &&\
    echo "Downloading OpenCV" $version  &&\
    wget -O OpenCV-$version.zip http://sourceforge.net/projects/opencvlibrary/files/opencv-unix/$version/opencv-"$version".zip/download  &&\
    echo "Installing OpenCV" $version  &&\
    unzip OpenCV-$version.zip  &&\
    cd opencv-$version  &&\
    mkdir /root/OpenCV/opencv-$version/build 

RUN cd /root/OpenCV/opencv-3.1.0/build &&\
    cmake -D CMAKE_BUILD_TYPE=RELEASE -D CMAKE_INSTALL_PREFIX=/usr/local -D WITH_TBB=ON -D BUILD_NEW_PYTHON_SUPPORT=ON -D WITH_V4L=ON -D INSTALL_C_EXAMPLES=ON -D INSTALL_PYTHON_EXAMPLES=ON -D BUILD_EXAMPLES=ON -D WITH_QT=ON -D WITH_OPENGL=ON -D -DBUILD_CUDA=ON -D CUDA_TOOLKIT_ROOT_DIR=/usr/local/cuda/lib64 ..   &&\
    make -j12 &&\
    sudo checkinstall -y &&\
    sudo sh -c 'echo "/usr/local/lib" > /etc/ld.so.conf.d/opencv.conf'  &&\
    sudo ldconfig  &&\
    echo "OpenCV $version ready to be used" 

#### Copy files
COPY root    /root
COPY etc     /etc
COPY var     /var

# Expose server port
EXPOSE 34448

# Set the application working directory
WORKDIR /home/docker-app

RUN ln -s /home/docker-app/digits/jobs /root/digits/digits/jobs

ENV TERM=xterm

# Run all processes through supervisord
CMD ["/usr/bin/supervisord", "-c", "/etc/supervisord.conf"]

# Logs do not need to be preserved when exporting
VOLUME ["/var/log"]

