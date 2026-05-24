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
    def faturar(conta_receber_id):

        conta = ContaReceber.objects.get(id = conta_receber_id)

        #Verificar se já existe saldo final para esta OS
        if ContaReceber.objects.filter(
            ordemServicoId=conta.ordemServicoId,
            tipo='SALDO_FINAL'
        ).exists():
            raise ValidationError(
                'Esta OS já foi faturada anteriormente.'
            )
        
        """Precisa verificar se existe uma ContaReceber
        da mesma OS com o tipo ENTRADA para reduzir o valor
        do saldo final"""
        
        #Gerar ContaReceber de saldo final
        saldo_final = ContaReceber.objects.create(
            clienteId = conta.clienteId,
            ordemServicoId = conta.ordemServicoId,
            tipo = 'SALDO_FINAL',
            valor = conta.valor - conta.valorPago,
            status = 'ABERTA',
            dataVencimento = _calcular_data_vencimento()
        )

        return saldo_final
