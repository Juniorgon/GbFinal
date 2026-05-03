from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='task',
            name='custom_type',
            field=models.CharField(blank=True, max_length=100, verbose_name='Outro Tipo de Tarefa'),
        ),
        migrations.AddField(
            model_name='historicaltask',
            name='custom_type',
            field=models.CharField(blank=True, max_length=100),
        ),
    ]
