FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y netcat-openbsd curl && rm -rf /var/lib/apt/lists/*

# Caminho relativo ao contexto de build (./backend/)
COPY auditoria_service/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# shared/ central — copiado de backend/shared/ para /app/shared/
COPY shared/ ./shared/

# Código do serviço
COPY auditoria_service/app/ .

COPY auditoria_service/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

EXPOSE 8009

ENTRYPOINT ["/entrypoint.sh"]
