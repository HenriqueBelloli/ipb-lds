#!/bin/sh

until nc -z db-auth 5432; do
  echo "Waiting for database..."
  sleep 1
done

python manage.py migrate --noinput
exec gunicorn auth_service.wsgi:application --bind 0.0.0.0:8001 --workers 2
