from django.db import models
import uuid

# Create your models here.

class LogAuditoria(models.Model):

    id = models.UUIDField(primary_key=True, auto_created=True, default=uuid.uuid4, editable=False)
    evento = models.CharField(max_length=100)
    servico = models.CharField(max_length=100),
    usuarioId = models.UUIDField(null=True, blank=True)
    delegacaoId = models.UUIDField(null=True, blank=True)
    payload = models.JSONField()
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']
    
    
