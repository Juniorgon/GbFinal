from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contracts', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='contract',
            name='custom_type',
            field=models.CharField(blank=True, max_length=100, verbose_name='Outro Tipo de Contrato'),
        ),
        migrations.AddField(
            model_name='historicalcontract',
            name='custom_type',
            field=models.CharField(blank=True, max_length=100),
        ),
    ]
