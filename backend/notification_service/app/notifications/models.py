from django.db import models
import uuid

# Create your models here.


class Notificacao(models.Model):

    TIPO_DEST_CHOICES = [
        ('USUARIO', 'Utilizador do sistema'),
        ('CLIENTE', 'Cliente externo'),
        ('SISTEMA', 'Notificacao de sistema - sem destinatario especifico')
    ]

    CANAL_CHOICES = [
        ('INTERNO', 'Registro interno - consultavel no frontend'),
        ('EMAIL', 'Envio de email via SMTP')
    ]


    id = models.UUIDField(primary_key=True, auto_created=True, default=uuid.uuid4, editable=False)
    destinatarioId = models.UUIDField(null=True)
    tipoDestinatario = models.CharField(max_length=20, choices=TIPO_DEST_CHOICES)
    canal = models.CharField(max_length=20, choices=CANAL_CHOICES)
    titulo = models.CharField(max_length=255)
    mensagem = models.TextField()
    evento = models.CharField(max_length=100)
    payload = models.JSONField()
    enviado = models.BooleanField(default=False)
    lida = models.BooleanField(default=False)
    erro = models.TextField(null=True)
    createdAt = models.DateTimeField(auto_now_add=True)
    
     