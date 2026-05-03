import django.db.models.deletion
import simple_history.models
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('branches', '0001_initial'),
        ('clients', '0001_initial'),
        ('processes', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Contract',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('type', models.CharField(choices=[
                    ('honorarios','Honorários Advocatícios'),('prestacao_servicos','Prestação de Serviços'),
                    ('consultoria','Consultoria Jurídica'),('retainer','Contrato de Retainer'),
                    ('sucumbencia','Honorários de Sucumbência'),('outro','Outro'),
                ], max_length=30, verbose_name='Tipo de Contrato')),
                ('title', models.CharField(max_length=200, verbose_name='Título')),
                ('description', models.TextField(verbose_name='Descrição Detalhada')),
                ('total_value', models.DecimalField(decimal_places=2, default=0, max_digits=15, verbose_name='Valor Total (R$)')),
                ('installments', models.PositiveIntegerField(default=1, verbose_name='Número de Parcelas')),
                ('payment_conditions', models.TextField(verbose_name='Condições de Pagamento')),
                ('status', models.CharField(choices=[
                    ('ativo','Ativo'),('concluido','Concluído'),('suspenso','Suspenso'),('cancelado','Cancelado'),
                ], default='ativo', max_length=15, verbose_name='Status')),
                ('judicial_type', models.CharField(choices=[
                    ('judicial','Judicial'),('extrajudicial','Extrajudicial'),('ambos','Ambos'),
                ], default='judicial', max_length=15, verbose_name='Judicial/Extrajudicial')),
                ('start_date', models.DateField(verbose_name='Data de Início')),
                ('end_date', models.DateField(verbose_name='Data de Término')),
                ('notes', models.TextField(blank=True, verbose_name='Observações Adicionais')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('branch', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='contracts', to='branches.branch')),
                ('client', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='contracts', to='clients.client', verbose_name='Cliente')),
                ('process', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='contracts', to='processes.process', verbose_name='Processo')),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
            options={'verbose_name': 'Contrato', 'verbose_name_plural': 'Contratos', 'ordering': ['-created_at']},
        ),
        migrations.CreateModel(
            name='HistoricalContract',
            fields=[
                ('id', models.BigIntegerField(auto_created=True, blank=True, db_index=True)),
                ('type', models.CharField(max_length=30)),
                ('title', models.CharField(max_length=200)),
                ('total_value', models.DecimalField(decimal_places=2, default=0, max_digits=15)),
                ('status', models.CharField(default='ativo', max_length=15)),
                ('start_date', models.DateField()),
                ('end_date', models.DateField()),
                ('created_at', models.DateTimeField(blank=True, editable=False)),
                ('updated_at', models.DateTimeField(blank=True, editable=False)),
                ('history_id', models.AutoField(primary_key=True, serialize=False)),
                ('history_date', models.DateTimeField(db_index=True)),
                ('history_change_reason', models.CharField(max_length=100, null=True)),
                ('history_type', models.CharField(choices=[('+','Created'),('~','Changed'),('-','Deleted')], max_length=1)),
                ('branch', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='branches.branch')),
                ('client', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='clients.client')),
                ('created_by', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to=settings.AUTH_USER_MODEL)),
                ('history_user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
            ],
            options={'verbose_name': 'historical contract', 'ordering': ['-history_date', '-history_id'], 'get_latest_by': ('history_date', 'history_id')},
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
    ]
