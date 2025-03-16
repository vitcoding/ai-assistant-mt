#!/usr/bin/env bash

gunicorn -c gunicorn.conf.py main:app

