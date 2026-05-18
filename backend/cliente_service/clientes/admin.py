from django.contrib import admin
from .models import Cliente, ClienteDelegacao

@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ['nome', 'nif', 'email', 'ativo', 'flagAssociado']
    search_fields = ['nome', 'nif', 'email']
    list_filter   = ['ativo', 'flagAssociado']


@admin.register(ClienteDelegacao)
class ClienteDelegacaoAdmin(admin.ModelAdmin):
    list_display = ['clienteId', 'delegacaoId', 'createdAt']
