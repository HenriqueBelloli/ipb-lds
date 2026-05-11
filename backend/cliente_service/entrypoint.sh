#!/bin/sh

# O 'set -e' faz com que o script pare imediatamente se qualquer comando falhar
set -e

# 1. Esperar que o PostgreSQL esteja realmente pronto
echo "A aguardar pelo PostgreSQL em $DB_HOST:5432..."
while ! nc -z $DB_HOST 5432; do
  sleep 0.5
done
echo "PostgreSQL está pronto!"

# 2. Aplicar migrações (cria as tabelas na base de dados)
echo "A aplicar migrações..."
pwd
ls -la
python manage.py makemigrations
python manage.py migrate

# 3. Iniciar o servidor Django
echo "A iniciar o servidor..."
python manage.py runserver 0.0.0.0:8003