from decimal import Decimal, InvalidOperation
from uuid import UUID

from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import Sum

from ..models import ContaReceber, Pagamento
from ..publishers import publish_pagamento_confirmado


class PagamentoService:

    @staticmethod
    @transaction.atomic
    def registrar(conta_id, valor, data, referencia, usuario_id):
        try:
            conta_id_uuid = UUID(conta_id)
        except ValueError:
            raise ValidationError('UUID invalido.')

        conta = ContaReceber.objects.select_for_update().get(id=conta_id_uuid)

        try:
            valor_decimal = Decimal(str(valor)).quantize(Decimal('0.01'))
        except (InvalidOperation, TypeError, ValueError):
            raise ValidationError('Valor de pagamento invalido.')

        if conta.status == 'PAGA':
            raise ValidationError('Essa duplicata ja esta totalmente paga.')

        if valor_decimal <= Decimal('0'):
            raise ValidationError('O valor do pagamento deve ser maior que zero.')

        saldo_aberto = conta.valor - conta.valorPago
        if valor_decimal > saldo_aberto:
            raise ValidationError('O valor do pagamento nao pode exceder o saldo em aberto.')

        pagamento = Pagamento.objects.create(
            contaReceberId=conta,
            usuarioId=usuario_id,
            valor=valor_decimal,
            data=data,
            referenciaBancaria=referencia,
        )

        total_pago = Pagamento.objects.filter(
            contaReceberId=conta.id,
        ).aggregate(total=Sum('valor'))['total'] or Decimal('0')

        conta.valorPago = total_pago
        if total_pago >= conta.valor:
            conta.status = 'PAGA'
        elif total_pago > 0:
            conta.status = 'PARCIAL'

        conta.save()

        if conta.status == 'PAGA':
            publish_pagamento_confirmado(conta=conta)

        return pagamento
