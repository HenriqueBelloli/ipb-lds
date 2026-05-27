#!/bin/sh
until nc -z ${DB_HOST:-postgres-servico} ${DB_PORT:-5432}; do
  echo "Waiting for database..."
  sleep 1
done
python manage.py migrate --noinput
exec gunicorn core.wsgi:application \
    --bind 0.0.0.0:8004 \
    --workers 2
