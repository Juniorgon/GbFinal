from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('processes', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='process',
            name='custom_type',
            field=models.CharField(blank=True, max_length=100, verbose_name='Outro Tipo de Processo'),
        ),
        migrations.AddField(
            model_name='historicalprocess',
            name='custom_type',
            field=models.CharField(blank=True, max_length=100),
        ),
    ]
