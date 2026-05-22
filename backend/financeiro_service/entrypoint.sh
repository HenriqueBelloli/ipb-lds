#!/bin/sh


python manage.py makemigrations
python manage.py migrate

gunicorn core.wsgi:application --bind 0.0.0.0:8006 --workers 2