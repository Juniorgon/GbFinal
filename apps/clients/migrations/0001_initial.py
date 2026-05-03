import django.db.models.deletion
import simple_history.models
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('branches', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Client',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=200, verbose_name='Nome Completo')),
                ('type', models.CharField(choices=[('fisica','Pessoa Física'),('juridica','Pessoa Jurídica')], default='fisica', max_length=10, verbose_name='Tipo')),
                ('cpf_cnpj', models.CharField(blank=True, max_length=20, verbose_name='CPF/CNPJ')),
                ('rg', models.CharField(blank=True, max_length=20, verbose_name='RG')),
                ('nationality', models.CharField(blank=True, default='Brasileira', max_length=50, verbose_name='Nacionalidade')),
                ('marital_status', models.CharField(blank=True, max_length=50, verbose_name='Estado Civil')),
                ('profession', models.CharField(blank=True, max_length=100, verbose_name='Profissão')),
                ('birth_date', models.DateField(blank=True, null=True, verbose_name='Data de Nascimento')),
                ('phone', models.CharField(max_length=20, verbose_name='Telefone')),
                ('phone2', models.CharField(blank=True, max_length=20, verbose_name='Telefone 2')),
                ('email', models.EmailField(blank=True, verbose_name='Email')),
                ('street', models.CharField(blank=True, max_length=200, verbose_name='Rua')),
                ('number', models.CharField(blank=True, max_length=10, verbose_name='Número')),
                ('complement', models.CharField(blank=True, max_length=100, verbose_name='Complemento')),
                ('district', models.CharField(blank=True, max_length=100, verbose_name='Bairro')),
                ('city', models.CharField(blank=True, max_length=100, verbose_name='Cidade')),
                ('state', models.CharField(blank=True, max_length=2, verbose_name='Estado')),
                ('zipcode', models.CharField(blank=True, max_length=10, verbose_name='CEP')),
                ('notes', models.TextField(blank=True, verbose_name='Observações')),
                ('is_active', models.BooleanField(default=True, verbose_name='Ativo')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('branch', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='clients', to='branches.branch', verbose_name='Filial')),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
            options={'verbose_name': 'Cliente', 'verbose_name_plural': 'Clientes', 'ordering': ['name']},
        ),
        migrations.CreateModel(
            name='HistoricalClient',
            fields=[
                ('id', models.BigIntegerField(auto_created=True, blank=True, db_index=True)),
                ('name', models.CharField(max_length=200)),
                ('type', models.CharField(max_length=10)),
                ('cpf_cnpj', models.CharField(blank=True, max_length=20)),
                ('phone', models.CharField(max_length=20)),
                ('city', models.CharField(blank=True, max_length=100)),
                ('state', models.CharField(blank=True, max_length=2)),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(blank=True, editable=False)),
                ('updated_at', models.DateTimeField(blank=True, editable=False)),
                ('history_id', models.AutoField(primary_key=True, serialize=False)),
                ('history_date', models.DateTimeField(db_index=True)),
                ('history_change_reason', models.CharField(max_length=100, null=True)),
                ('history_type', models.CharField(choices=[('+','Created'),('~','Changed'),('-','Deleted')], max_length=1)),
                ('branch', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='branches.branch')),
                ('created_by', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to=settings.AUTH_USER_MODEL)),
                ('history_user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
            ],
            options={'verbose_name': 'historical client', 'verbose_name_plural': 'historical clients', 'ordering': ['-history_date', '-history_id'], 'get_latest_by': ('history_date', 'history_id')},
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
    ]
