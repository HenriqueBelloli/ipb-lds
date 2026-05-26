FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y netcat-openbsd curl && rm -rf /var/lib/apt/lists/*

# Dependências — caminho relativo ao contexto de build (./backend/)
COPY auth_service/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# shared/ central — copiado de backend/shared/ para /app/shared/
COPY shared/ ./shared/

# Código do serviço
COPY auth_service/app/ .

# Entrypoint na raiz do container
COPY auth_service/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

EXPOSE 8001

ENTRYPOINT ["/entrypoint.sh"]
