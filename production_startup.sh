#!/bin/bash
cd src
mkdir /home/site/wwwroot/src/config/static
python manage.py collectstatic --noinput
python manage.py migrate
gunicorn --bind=0.0.0.0 --timeout 600 config.wsgi:application
