SHELL:=/bin/bash
DOCKER_VERSION:=v1
DOCKER_REGISTRY_STAGE:=justonecommand/cloudflare-status-exporter
all: build upload

build:
	docker build -t ${DOCKER_REGISTRY_STAGE}:${DOCKER_VERSION} .
upload:
	docker push ${DOCKER_REGISTRY_STAGE}:${DOCKER_VERSION}
