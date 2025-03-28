#!/bin/bash

# docker pull python:3.10-slim
# docker pull rabbitmq:latest

cd docker
docker compose -f compose.yml   up  --build  		\
       barometre_web 					\
       barometre_celery_worker 				\
       barometre_celery_beat 				\
       barometre_rabbitmq

# For admin commands, start a shell, use docker-web-bash.sh.
