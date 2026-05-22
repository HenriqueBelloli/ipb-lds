from django.servicos.exceptions import ValidationError

def validar_percentual_entrada(value):
    if value < 0 or value > 100:
        raise ValidationError('percentualEntrada deve ser um valor entre 0 e 100.')
def validar_precos(preco_associado, preco_nao_associado):
    if preco_associado <= 0:
        raise ValidationError('precoAssociado deve ser maior que zero.')
    if preco_nao_associado <= 0:
        raise ValidationError('precoNaoAssociado deve ser maior que zero.')
    if preco_associado > preco_nao_associado:
        raise ValidationError('precoAssociado não pode ser maior que precoNaoAssociado.')