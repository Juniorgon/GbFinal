from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='Branch',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='Nome')),
                ('address', models.CharField(blank=True, max_length=200, verbose_name='Endereço')),
                ('phone', models.CharField(blank=True, max_length=20, verbose_name='Telefone')),
                ('email', models.EmailField(blank=True, verbose_name='Email')),
                ('city', models.CharField(blank=True, max_length=100, verbose_name='Cidade')),
                ('state', models.CharField(blank=True, max_length=2, verbose_name='Estado')),
                ('admin_name', models.CharField(blank=True, max_length=100, verbose_name='Admin')),
                ('is_active', models.BooleanField(default=True, verbose_name='Ativa')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'verbose_name': 'Filial',
                'verbose_name_plural': 'Filiais',
                'ordering': ['name'],
            },
        ),
    ]
