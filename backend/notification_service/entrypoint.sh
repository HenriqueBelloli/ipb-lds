#!/bin/sh

echo "Efetuando migracoes..."
python manage.py migrate
echo "Migracoes concluidas, iniciando gunicorn..."

gunicorn core.wsgi:application --bind 0.0.0.0:8009 --workers 2