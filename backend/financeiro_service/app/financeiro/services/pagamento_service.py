from django.db import transaction
from ..models import ContaReceber, Pagamento
from django.core.exceptions import ValidationError
from ..publishers import publish_pagamento_confirmado
from uuid import UUID
from django.db.models import Sum

class PagamentoService:

    @staticmethod
    @transaction.atomic
    def registrar(conta_id, valor, data, referencia, usuario_id):

        try:
            conta_id_uuid = UUID(conta_id)
        except ValidationError:
            raise ValidationError('UUID invalido')

        conta = ContaReceber.objects.select_for_update().get(id=conta_id_uuid)

        if conta.status == 'PAGA':
            raise ValidationError('Essa duplicata já está totalmente paga.')
        
        if valor <=0:
            raise ValidationError('O valor do pagamento deve ser maior que zero.')
        
        #registrar o pagamento
        pagamento = Pagamento.objects.create(
            contaReceberId = conta,
            usuarioId = usuario_id,
            valor=valor,
            data=data,
            referenciaBancaria = referencia
        )

        #recalcular o total pago
        total_pago = Pagamento.objects.filter(
            contaReceberId = conta.id
        ).aggregate(total=Sum('valor'))['total'] or 0

        #atualizar status da conta
        conta.valorPago = total_pago
        if total_pago >= conta.valor:
            conta.status = 'PAGA'
        elif total_pago > 0:
            conta.status = 'PARCIAL'
        
        conta.save()

        if conta.status == 'PAGA':
            publish_pagamento_confirmado(conta=conta)
        
        return pagamento