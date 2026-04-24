import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='Credencial',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('usuarioId', models.UUIDField(unique=True)),
                ('delegacaoId', models.UUIDField()),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('passwordHash', models.CharField(max_length=255)),
                ('perfil', models.CharField(choices=[('OPERADOR', 'Operador'), ('GESTOR', 'Gestor'), ('FINANCEIRO', 'Financeiro'), ('DIRECAO', 'Direção'), ('ADMINISTRADOR', 'Administrador')], max_length=20)),
                ('ativo', models.BooleanField(default=True)),
                ('createdAt', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'db_table': 'credenciais',
            },
        ),
    ]
