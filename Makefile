SHELL := /bin/bash

.PHONY: service-up service-rm service-clear service-setup

service-up:
	@(export $(grep -v '^#' ./scripts/sample.env | xargs) > /dev/null 2>&1 && \
	docker-compose --env-file ./scripts/sample.env -f ./service/docker-compose.yml up -d && \
	./scripts/setup-grafana.sh)

service-down:
	docker-compose --env-file ./scripts/sample.env -f ./service/docker-compose.yml down && \
	echo "removed grafana and postgres services"

service-clear:
	docker-compose --env-file ./scripts/sample.env -f ./service/docker-compose.yml down && \
	echo "removed grafana and postgres services" && \
	sudo rm -rf data/postgres/* && \
	sudo rm -rf data/grafana/* && \
	echo "cleared data folders"

service-setup:
	sudo chmod -R 777 data/postgres/ && \
	sudo chmod -R 777 data/grafana/
