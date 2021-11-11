#!/bin/bash

until nc -z ${BROKER_HOST} ${BROKER_PORT}; do
    echo "$(date) - waiting for rabbitmq PubSub ..."
    sleep 1
done

export PYTHONPATH=$PYTHONPATH:/app

echo "Content of PYTHONPATH variable $PYTHONPATH"

echo Starting CTI Receiver Server.
exec python3 cti_receiver/app.py