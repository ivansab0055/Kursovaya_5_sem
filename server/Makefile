.PHONY: build-no-cache bmc rm-images rmi rm-volumes rmv rm-containers rmc rm-used-images rmui rm-used-volumes rmuv clear-cache clc clear-all cla

DEFAULT_VALUE := dev
value := $(or $(word 2, $(MAKECMDGOALS)), $(DEFAULT_VALUE))
COMPOSE_FILE := docker-compose-$(value).yml

build:
	@echo "Build app with $(COMPOSE_FILE)"
	docker-compose -f $(COMPOSE_FILE) build
build-no-cache bnc:
	@echo "Build app without cache with $(COMPOSE_FILE)"
	docker-compose -f $(COMPOSE_FILE) build --no-cache

run:
	@echo "Start app with $(COMPOSE_FILE)"
	docker-compose -f $(COMPOSE_FILE) up -d

rm-images rmi:
	@echo "All UNUSED images will be removed"
	docker image prune

rm-all-images rmai:
	@echo "All USED/UNUSED images will be removed - [use in Unix bash]"
	docker image rm $(docker image ls -q)

rm-volumes rmv:
	@echo "All UNUSED volumes will be removed"
	docker volume prune

rm-all-volumes rmav:
	@echo "All USED/UNUSED volumes will be removed - [use in Unix bash]"
	docker volume rm $(docker volume ls -q)

rm-containers rmc:
	@echo "All UNUSED containers will be removed"
	docker container prune

clear-cache clc:
	@echo "Clear cache"
	docker builder prune

clear-all cla:
	@echo "Remove all unused containers, networks, images (both dangling and unused), and optionally, volumes"
	docker system prune -a --volumes

df:
	@echo "Docker disk usage"
	docker system df

size:
	@echo "Docker containers size"
	docker ps -s

stop:
	@echo "Stop all containers - [use in Unix bash]"
	@docker stop $$(docker ps -q) || true

clear:
	@echo "Rm unused images, containers, volumes"
	docker image prune -f
	docker volume prune -f
	docker container prune -f

info:
	@echo "Docker Server Version: $$(docker version --format '{{.Server.Version}}') $(shell docker version --format '{{.Server.Platform.Name}}')"
logs:
	@echo "Show logs"
	docker ps -q | xargs -L 1 docker logs

help:
	@echo "build              : Build docker-compose from file"
	@echo "build-no-cache|bnc : Build docker-compose from file without cache"
	@echo "run                : Run docker container"
	@echo "rm-images rmi      : All UNUSED images will be removed"
	@echo "rm-all-images rmai : All USED/UNUSED images will be removed - [use in Unix bash]"
	@echo "rm-volumes rmv     : All UNUSED volumes will be removed"
	@echo "rm-all-volumes rmav: All USED/UNUSED volumes will be removed - [use in Unix bash]"
	@echo "rm-containers rmc  : All UNUSED containers will be removed"
	@echo "clear-cache clc    : Clear cache"
	@echo "clear-all cla      : Remove all unused containers, networks, images (both dangling and unused), and optionally, volumes"
	@echo "df                 : Docker disk usage"
	@echo "size               : Docker containers size"
	@echo "stop               : Stop all containers"
	@echo "clear              : Rm unused images, containers, volumes"
	@echo "info               : Show docker version"
	@echo "logs               : Show docker logs"

# Игнорируем все дополнительные цели, чтобы make не пытался их выполнять
%:
	@:
