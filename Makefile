# Var Definition
#
DOMAIN=${MX_domain}
CERT_DIR=${MX_certspath}
CERT_GEN=bin/minica

.PHONY: help certs build push all

help:
	    @echo "Makefile arguments:"
	    @echo ""
	    @echo "pyvers - Python Image Base Version, default is: 3.11-slim-bullseye"
	    @echo ""
	    @echo "Makefile commands:"
	    @echo "certs"
	    @echo "build"
	    @echo "push"
	    @echo "all"

.DEFAULT_GOAL := all

certs:
	@echo "Building Cert generator"
	@([ ! -d bin ] && mkdir -p bin) || true
	@([ ! -f $(CERT_GEN) ] && (cd minica; go build -o ../bin) ) || true
	@echo "Generating Certs"
	@([ ! -d $(CERT_DIR) ] && mkdir -p $(CERT_DIR)) || true
	@cd $(CERT_DIR) && ../$(CERT_GEN) \
		-ca-cert root-ca.pem \
		-ca-key key-ca.pem \
		-domains '$(DOMAIN),*.$(DOMAIN),localhost' \
		-ip-addresses 127.0.0.1 || true
build:
	$(MAKE) -C server build
	$(MAKE) -C client build

push:
	$(MAKE) -C server push	
	$(MAKE) -C client push

all: certs build 
