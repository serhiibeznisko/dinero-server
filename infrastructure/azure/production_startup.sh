#!/bin/bash
cd src
#mkdir -p /code/src/config/static && python manage.py collectstatic --noinput
python manage.py migrate
#python manage.py compilemessages
gunicorn --bind 0.0.0.0:$PORT config.wsgi:application
