FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y netcat-openbsd curl \
    && rm -rf /var/lib/apt/lists/*

# Caminho relativo ao contexto de build (./backend/)
COPY servico-service/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# shared/ central
COPY shared/ ./shared/

# Código do serviço
COPY servico-service/app .

COPY servico-service/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

EXPOSE 8004

ENTRYPOINT ["/entrypoint.sh"]
