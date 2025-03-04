#!/bin/bash

while ! nc -z $POSTGRES_HOST $POSTGRES_PORT; do
      sleep 1
done
while ! nc -z $REDIS_HOST $REDIS_PORT; do
      sleep 1
done
while ! nc -z $ELASTICSEARCH_HOST $ELASTICSEARCH_PORT; do
      sleep 1
done

python main.py