#!/usr/bin/env bash

set -e


while ! nc -z auth-nginx 80; do
    sleep 3;
done

sleep 5

pytest
