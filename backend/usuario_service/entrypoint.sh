#!/bin/sh

until nc -z ${DB_HOST:-db-usuario} ${DB_PORT:-5432}; do
  echo "Waiting for database..."
  sleep 1
done

python manage.py migrate --noinput
python manage.py seed
exec gunicorn core.wsgi:application --bind 0.0.0.0:8002 --workers 2