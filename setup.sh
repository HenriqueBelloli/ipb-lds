#!/bin/bash

echo "Preparando ambiente local..."

# Criar .env files copiando dos templates
if [ ! -f .env.usuario-service ]; then
  echo "Criando .env.usuario-service..."
  cp .env.example.usuario-service .env.usuario-service || echo "aviso: .env.example.usuario-service não encontrado"
fi

if [ ! -f .env.usuario-service.db ]; then
  echo "Criando .env.usuario-service.db..."
  cat > .env.usuario-service.db << 'ENVDB'
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=usuario_db
ENVDB
fi

if [ ! -f backend/auth_service/.env ]; then
  echo "Criando backend/auth_service/.env..."
  cp backend/auth_service/.env.example backend/auth_service/.env
fi

echo "Setup concluído!"
echo ""
echo "Próximo passo:"
echo "  docker-compose up -d"
