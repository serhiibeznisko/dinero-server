#!/bin/bash
cd src
touch test.txt
mkdir -p /home/site/wwwroot/src/config/static && python manage.py collectstatic --noinput
python manage.py migrate
