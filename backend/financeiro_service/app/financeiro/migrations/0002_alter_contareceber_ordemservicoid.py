from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('financeiro', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='contareceber',
            name='ordemServicoId',
            field=models.UUIDField(blank=True, editable=False, null=True),
        ),
    ]
