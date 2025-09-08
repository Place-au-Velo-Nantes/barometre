#!/bin/bash

export SSH_USER=$LOGNAME

action="$1"
shift
case "$action" in
    run)
	docker compose -f compose.yml   up  --build	\
	       barometre_web 				\
	       barometre_celery_worker 			\
	       barometre_celery_beat 			\
	       barometre_rabbitmq
	;;
    test)
	docker compose   run --build  barometre_test "$@"
	;;
    sh)
	CONTAINER_ID=$(docker ps -qf "name=docker-barometre_web")
	if [ ! -z "$CONTAINER_ID" ]; then
	  echo "Container is already running.  Attaching shell..."
	  docker exec -ti "$CONTAINER_ID" /bin/bash
	else
	  echo "Container is not running.  Starting the container in shell mode..."
	  docker compose run --build --rm barometre_web /bin/bash
	fi
	;;
    *)
	echo "Unrecognised action: \"$action\"."
        ;;
esac
