import uuid
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Cliente',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('nome', models.CharField(max_length=255)),
                ('telefone', models.CharField(blank=True, max_length=20, null=True)),
                ('email', models.EmailField(blank=True, max_length=254, null=True)),
                ('morada', models.CharField(blank=True, max_length=500, null=True)),
                ('flagAssociado', models.BooleanField(default=False)),
                ('ativo', models.BooleanField(default=True)),
                ('nif', models.CharField(max_length=20, unique=True)),
                ('createdAt', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'db_table': 'cliente',
                'ordering': ['nome'],
            },
        ),
        migrations.CreateModel(
            name='ClienteDelegacao',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('clienteId', models.ForeignKey(db_column='clienteId', on_delete=django.db.models.deletion.CASCADE, related_name='delegacoes', to='clientes.cliente')),
                ('delegacaoId', models.UUIDField()),
                ('createdAt', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'db_table': 'cliente_delegacao',
                'ordering': ['-createdAt'],
            },
        ),
        migrations.AlterUniqueTogether(
            name='clientedelegacao',
            unique_together={('clienteId', 'delegacaoId')},
        ),
    ]
