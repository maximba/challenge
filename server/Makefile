#Dockerfile vars
pyvers=3.11-slim-bullseye

#vars
IMAGENAME=pyserver
IMAGE_VER=1.0.0
REPO=maximba
IMAGEFULLNAME=${REPO}/${IMAGENAME}:${IMAGE_VER}

.PHONY: help build push all

help:
	    @echo "Makefile arguments:"
	    @echo ""
	    @echo "pyversion - Python Version"
	    @echo "pyserver - pyclient version"
	    @echo ""
	    @echo "Makefile commands:"
	    @echo "build"
	    @echo "push"
	    @echo "all"

.DEFAULT_GOAL := all

build:
	    @docker build --build-arg pyvers=${pyvers} -t ${IMAGEFULLNAME} .

push:
	    @docker push ${IMAGEFULLNAME}

all: build push
