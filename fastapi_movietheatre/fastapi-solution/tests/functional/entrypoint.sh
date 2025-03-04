#!/usr/bin/env bash

set -e

while ! nc -z mt-cache 6379; do 
    sleep 1; 
done 

while ! nc -z mt-search-db 9200; do 
    sleep 1; 
done 

while ! nc -z mt-search-service 8000; do 
    sleep 1; 
done 

pytest
