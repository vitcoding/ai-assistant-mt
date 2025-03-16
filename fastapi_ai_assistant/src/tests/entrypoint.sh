#!/usr/bin/env bash

set -e


while ! nc -z nginx 80; do
    sleep 3;
done

sleep 3

pytest
