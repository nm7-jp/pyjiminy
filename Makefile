NAME=pyjiminy
VERSION=0.0.1
MAKEFLAGS += --warn-undefined-variables
.DEFAULT_GOAL := help
envname = .env
fileexists = $(shell ls -a | grep $(envname))

.PHONY: build
build: ## build docker image
	docker build --tag $(NAME):$(VERSION) .

.PHONY: start
start: ## start docker container
ifeq ($(fileexists),$(envname))
	docker run --interactive --tty --detach --rm --env-file ${PWD}/$(envname) --name $(NAME) $(NAME):$(VERSION)
else
	docker run --interactive --tty --detach --rm --name $(NAME) $(NAME):$(VERSION)
endif

.PHONY: stop
stop: ## remove docker container
	docker rm --force $(NAME)

.PHONY: restart
restart: stop start ## restart docker container

.PHONY: attach
attach: ## debug 
	docker exec --interactive --tty $(NAME) /bin/bash

.PHONY: clean
clean: ## remove docker image
	docker rmi --force $(NAME):$(VERSION)

.PHONY: inspect
inspect: ## inspect container information
	docker inspect $(NAME)

.PHONY: logs
logs: ## inspect container log
	docker logs $(NAME)

.PHONY: help
help: ## Print this help
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Targets:'
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)