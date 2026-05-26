#!/bin/sh

#necessário para o django não tentar acessar o bd antes de estar pronto
until nc -z usuario-service-db 5432; do
  echo "Waiting for database..."
  sleep 1
done

python manage.py makemigrations
python manage.py migrate
python manage.py runserver 0.0.0.0:8002