from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('financial', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='transaction',
            name='category',
            field=models.CharField(max_length=100, verbose_name='Categoria'),
        ),
        migrations.AlterField(
            model_name='historicaltransaction',
            name='category',
            field=models.CharField(max_length=100),
        ),
    ]
