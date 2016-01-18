SHELL=bash

DOCKERFILES=${wildcard */Dockerfile}
DOCKERDIR=${DOCKERFILES:/Dockerfile=}

build: ${DOCKERDIR:%=%.build}

%.build:
	echo -e "\n\e[7m${@:.build=}\e[0m\n"
	docker build --rm --tag=jguiraudet/${@:.build=} ${@:.build=}

# Dependencies
letsencrypt.build: jekyll-dev.build
