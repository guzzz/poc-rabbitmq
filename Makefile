#!/bin/bash
.PHONY: default
.SILENT:


default:

start:
	docker-compose up -d

start_with_logs:
	docker-compose up

stop:
	docker-compose down
	make clear

start_system1_separate:
	docker-compose down api_system_1
	docker-compose up api_system_1

start_system2_separate:
	docker-compose down api_system_2
	docker-compose up api_system_2

start_queue_separate:
	docker-compose down queue_consumer
	docker-compose up queue_consumer

clear:
	redis-cli FLUSHALL
	docker volume prune
	docker volume rm db_postgres_1 db_postgres_2 db_postgres_endput mongodb-data redis-data

prune:
	docker container prune
	docker image prune
	docker volume prune
