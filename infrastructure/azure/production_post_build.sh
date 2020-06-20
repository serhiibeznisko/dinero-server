#!/bin/bash
cd src
#mkdir -p /code/src/config/static && python manage.py collectstatic --noinput
python manage.py migrate
