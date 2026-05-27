import requests
from django.utils import timezone
import os
from ..models import ConfiguracaoFinanceira, ContaReceber
from decimal import Decimal
import json
from django.db import transaction
from ..publishers import publish_mensalidades_geradas

class MensalidadeService:

    CLIENTE_SERVICE_URL = os.environ.get(
        'CLIENTE_SERVICE_URL',
        'http://cliente-service:8003'
    )

    @staticmethod
    def obter_valor_mensalidade():
        config = ConfiguracaoFinanceira.objects.filter(
            chave = "VALOR_MENSALIDADE"
        ).first()

        if not config:
            raise ValueError(
                'Valor de mensalidade não configurado.'
            )
        
        return Decimal(config.valor)
    
    @staticmethod
    def buscar_associados_ativos(token):
        try:
            response = requests.get(
                f"{MensalidadeService.CLIENTE_SERVICE_URL}"
                "/api/clientes/?flagAssociado=true&ativo=true&page_size=1000",
                headers={
                    "Authorization": f"Bearer {token}"
                },
                timeout=10
            )

            response.raise_for_status()
            return response.json().get('results', [])
        
        except requests.exceptions.RequestException:
            return []
    
    @staticmethod
    @transaction.atomic
    def gerar_mensalidades(token=None):
        hoje = timezone.now().date()
        valor = MensalidadeService.obter_valor_mensalidade()
        associados = MensalidadeService.buscar_associados_ativos(token)

        geradas = 0
        ignoradas = 0

        for associado in associados:
            cliente_id = associado['id']

            #Verificar se já existe mensalidade para o mês vigente
            ja_existe = ContaReceber.objects.filter(
                clienteId=cliente_id,
                tipo='MENSALIDADE',
                dataVencimento__year=hoje.year,
                dataVencimento__month=hoje.month
            ).exists()

            if ja_existe:
                ignoradas += 1
                continue

            ContaReceber.objects.create(
                clienteId=cliente_id,
                ordemServicoId=None,
                tipo = "MENSALIDADE",
                valor = valor,
                status = "ABERTA",
                dataVencimento = hoje.replace(day=10)
            )

            geradas += 1
        
        publish_mensalidades_geradas(
            mesReferencia=f"{hoje.year}-{hoje.month:02d}",
            totalGeradas = str(geradas),
            totalIgnoradas = str(ignoradas)
        )

        return {'geradas' : geradas, 'ignoradas': ignoradas}

