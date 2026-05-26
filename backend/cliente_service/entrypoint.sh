#!/bin/sh
set -e

echo "A aguardar pelo PostgreSQL..."
python -c "
import socket, time, os
host = os.environ.get('POSTGRES_HOST', 'cliente-service-db')
port = int(os.environ.get('POSTGRES_PORT', 5432))
while True:
    try:
        s = socket.create_connection((host, port), timeout=1)
        s.close()
        print('PostgreSQL esta pronto!')
        break
    except Exception as e:
        print('A aguardar...', e)
        time.sleep(0.5)
"

echo "A aplicar migracoes..."
python manage.py makemigrations --noinput
python manage.py migrate --noinput

echo 'A recolher ficheiros estaticos...'
python manage.py collectstatic --noinput

echo "A iniciar o servidor..."
gunicorn cliente_service.wsgi:application --bind 0.0.0.0:8003 --workers 2