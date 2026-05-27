import uuid
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='Servico',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('nome', models.CharField(max_length=255)),
                ('descricao', models.TextField(blank=True, null=True)),
                ('flagBonificavel', models.BooleanField(default=False)),
                ('ativo', models.BooleanField(default=True)),
                ('createdAt', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'db_table': 'servico',
                'ordering': ['nome'],
            },
        ),
        migrations.CreateModel(
            name='ServicoDelegacao',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('delegacaoId', models.UUIDField()),
                ('precoAssociado', models.DecimalField(decimal_places=2, max_digits=10)),
                ('precoNaoAssociado', models.DecimalField(decimal_places=2, max_digits=10)),
                ('percentualEntrada', models.DecimalField(decimal_places=2, default=0, max_digits=5)),
                ('ativo', models.BooleanField(default=True)),
                ('createdAt', models.DateTimeField(auto_now_add=True)),
                ('servicoId', models.ForeignKey(
                    db_column='servicoId',
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='delegacoes',
                    to='servicos.Servico',
                )),
            ],
            options={
                'db_table': 'servico_delegacao',
                'ordering': ['servicoId__nome'],
            },
        ),
        migrations.AlterUniqueTogether(
            name='servicodelegacao',
            unique_together={('delegacaoId', 'servicoId')},
        ),
    ]
