FROM python:3.12-slim

WORKDIR /app
COPY docker/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY usuario_service .

COPY docker/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
RUN apt-get update && apt-get install -y netcat-openbsd

ENTRYPOINT ["/entrypoint.sh"]