#!/bin/bash
cd src
mkdir -p /home/site/wwwroot/src/config/static && python manage.py collectstatic --noinput
python manage.py migrate
