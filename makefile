SHELL=bash

DOCKERFILES=${wildcard */Dockerfile}
DOCKERDIR=${DOCKERFILES:/Dockerfile=}

build: ${DOCKERDIR:%=%.build}

%.build:
	@echo -e "\n\e[7m${@:.build=}\e[0m\n"
	docker build --rm --tag=jguiraudet/${@:.build=} ${@:.build=}


tensorflow-gpu.build:
	@echo -e "\n\e[7m${@:.build=}\e[0m\n"
	#b.gcr.io/tensorflow/tensorflow-gp
	docker build --rm --tag=jguiraudet/tensorflow-gpu -f ../../tensorflow/tensorflow/tools/docker/Dockerfile.devel-gpu ../../tensorflow/tensorflow/tools/docker


gazebo.build:
	docker build -t gazebo:gzserver6                     ../osrf/gazebo/gazebo6/gzserver6
	docker build -t gazebo:gzclient6                     ../osrf/gazebo/gazebo6/gzclient6
	docker build -t gazebo:libgazebo6                    ../osrf/gazebo/gazebo6/libgazebo6
	docker build -t gazebo:gzweb6                        ../osrf/gazebo/gazebo6/gzweb6

gazebo7.build:
	docker build -t gazebo:gzserver7                     ../osrf/gazebo/gazebo7/gzserver7
	#docker build -t gazebo:gzclient7                     ../osrf/gazebo/gazebo7/gzclient7
	docker build -t gazebo:libgazebo7                    ../osrf/gazebo/gazebo7/libgazebo7
	docker build -t gazebo:gzweb7                        ../osrf/gazebo/gazebo7/gzweb7



# Dependencies
letsencrypt.build: jekyll-dev.build


