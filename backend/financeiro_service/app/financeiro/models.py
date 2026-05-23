from django.db import models
import uuid

# Create your models here.
TIPO_CHOICES = [
    ('ENTRADA', 'Entrada'),
    ('SALDO_FINAL', 'Saldo Final'),
    ('MENSALIDADE', 'Mensalidade')
]

STATUS_CHOICES = [
    ('ABERTA', 'Aberta'),
    ('PARCIAL', 'Parcial'),
    ('PAGA', 'Paga'),
    ('VENCIDA', 'Vencida')
]

class ContaReceber(models.Model):

    id = models.UUIDField(primary_key=True, auto_created=True, default=uuid.uuid4, editable=False)
    clienteId = models.UUIDField()
    ordemServicoId = models.UUIDField(null=True, editable=True)
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    valor = models.DecimalField(max_digits=10, decimal_places=2)
    valorPago = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    dataVencimento = models.DateField()
    createdAt = models.DateTimeField(auto_now_add=True)

class Pagamento(models.Model):

    id = models.UUIDField(primary_key=True, auto_created=True, default=uuid.uuid4, editable=False)
    contaReceberId = models.ForeignKey(ContaReceber, on_delete=models.PROTECT, related_name='pagamentos')
    usuarioId = models.UUIDField(null=True)
    valor = models.DecimalField(max_digits=10, decimal_places=2)
    data = models.DateField()
    referenciaBancaria = models.CharField(max_length=255, null=True)
    createdAt = models.DateTimeField(auto_now_add=True)

class ConfiguracaoFinanceira(models.Model):

    id = models.UUIDField(primary_key=True, auto_created=True, default=uuid.uuid4)
    chave = models.CharField(max_length=100, unique=True)
    valor = models.CharField(max_length=255)
    atualizadoEm = models.DateTimeField(auto_now=True)
    usuarioId = models.UUIDField(null=True)

