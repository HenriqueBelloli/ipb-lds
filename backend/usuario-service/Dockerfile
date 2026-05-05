FROM python:3.12-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ .

COPY dentrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
RUN apt-get update && apt-get install -y netcat-openbsd

EXPOSE 8002

CMD ["gunicorn", "core.wsgi:application", "--bind", "0.0.0.0:8002", "--workers", "2"]
