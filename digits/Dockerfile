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


RUN DEBIAN_FRONTEND=noninteractive apt-get -qqy install \
        nginx \
        supervisor && \
    mkdir /var/log/digits


#### Copy files
COPY test.sh /root/test.sh
COPY etc     /etc
COPY var     /var

# Expose server port
EXPOSE 34448
# Set ~/digits as working directory
WORKDIR /root/digits

# Run all processes through supervisord
CMD ["/usr/bin/supervisord", "-c", "/etc/supervisord.conf"]

# Logs do not need to be preserved when exporting
VOLUME ["/var/log"]

