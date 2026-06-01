import uuid
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='OrdemServico',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('clienteId', models.UUIDField()),
                ('delegacaoContratacaoId', models.UUIDField()),
                ('delegacaoExecucaoId', models.UUIDField()),
                ('usuarioCriacaoId', models.UUIDField()),
                ('status', models.CharField(
                    choices=[
                        ('ORCAMENTO', 'Orçamento'),
                        ('AGUARDA_APROVACAO', 'Aguarda Aprovação'),
                        ('PAGAMENTO_PENDENTE', 'Pagamento Pendente'),
                        ('A_EXECUTAR', 'A Executar'),
                        ('EM_EXECUCAO', 'Em Execução'),
                        ('CONCLUIDO', 'Concluído'),
                        ('FATURADO', 'Faturado'),
                        ('CANCELADO', 'Cancelado'),
                    ],
                    default='ORCAMENTO',
                    max_length=30,
                )),
                ('valorTotal', models.DecimalField(decimal_places=2, max_digits=10)),
                ('tipoPreco', models.CharField(
                    choices=[('ASSOCIADO', 'Associado'), ('NAO_ASSOCIADO', 'Não Associado')],
                    max_length=20,
                )),
                ('motivoCancelamento', models.TextField(blank=True, null=True)),
                ('createdAt', models.DateTimeField(auto_now_add=True)),
                ('updatedAt', models.DateTimeField(auto_now=True)),
            ],
            options={
                'db_table': 'ordem_servico',
                'ordering': ['-createdAt'],
            },
        ),
        migrations.CreateModel(
            name='OrdemServicoServico',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('ordemServicoId', models.ForeignKey(
                    db_column='ordemServicoId',
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='itens',
                    to='ordens.ordemservico',
                )),
                ('servicoId', models.UUIDField()),
                ('servicoDelegacaoId', models.UUIDField()),
                ('precoAplicado', models.DecimalField(decimal_places=2, max_digits=10)),
                ('bonificado', models.BooleanField(default=False)),
                ('createdAt', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'db_table': 'ordem_servico_servico',
            },
        ),
        migrations.CreateModel(
            name='OrdemServicoHistorico',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('ordemServicoId', models.ForeignKey(
                    db_column='ordemServicoId',
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='historico',
                    to='ordens.ordemservico',
                )),
                ('usuarioId', models.UUIDField(blank=True, null=True)),
                ('statusAnterior', models.CharField(blank=True, max_length=30, null=True)),
                ('statusNovo', models.CharField(max_length=30)),
                ('observacao', models.TextField(blank=True, null=True)),
                ('createdAt', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'db_table': 'ordem_servico_historico',
                'ordering': ['createdAt'],
            },
        ),
    ]
