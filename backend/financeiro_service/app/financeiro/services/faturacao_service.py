from django.db import transaction
from ..models import ContaReceber
from django.core.exceptions import ValidationError
from datetime import date, timedelta

def _avancar_dia_util(data : date):
    while data.weekday() in (5,6):
        data += timedelta(days=1)
    
    return data

def _calcular_data_vencimento() -> date:
    data = date.today() + timedelta(days=30)
    
    return _avancar_dia_util(data)

class FaturacaoService:

    @staticmethod
    @transaction.atomic
    def faturar(conta_receber_id, valor_restante=None):
        conta = ContaReceber.objects.get(id=conta_receber_id)

        if ContaReceber.objects.filter(
            ordemServicoId=conta.ordemServicoId,
            tipo='SALDO_FINAL'
        ).exists():
            raise ValidationError('Esta OS já foi faturada anteriormente.')

        if valor_restante is None:
            raise ValidationError(
                'valorRestante é obrigatório para criar o saldo final. '
                'Forneça o valor restante a receber após a entrada.'
            )

        saldo_final = ContaReceber.objects.create(
            clienteId=conta.clienteId,
            ordemServicoId=conta.ordemServicoId,
            tipo='SALDO_FINAL',
            valor=valor_restante,
            status='ABERTA',
            dataVencimento=_calcular_data_vencimento()
        )

        return saldo_final
