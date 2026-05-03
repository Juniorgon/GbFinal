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
            name='Transaction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('type', models.CharField(choices=[('receita','Receita'),('despesa','Despesa')], max_length=10, verbose_name='Tipo')),
                ('category', models.CharField(max_length=30, verbose_name='Categoria')),
                ('description', models.TextField(verbose_name='Descrição')),
                ('value', models.DecimalField(decimal_places=2, max_digits=15, verbose_name='Valor')),
                ('due_date', models.DateField(verbose_name='Vencimento')),
                ('payment_date', models.DateField(blank=True, null=True, verbose_name='Data de Pagamento')),
                ('status', models.CharField(choices=[
                    ('pendente','Pendente'),('pago','Pago'),('vencido','Vencido'),('cancelado','Cancelado'),
                ], default='pendente', max_length=15, verbose_name='Status')),
                ('notes', models.TextField(blank=True, verbose_name='Observações')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('branch', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='transactions', to='branches.branch')),
                ('client', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='transactions', to='clients.client', verbose_name='Cliente')),
                ('process', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='transactions', to='processes.process', verbose_name='Processo')),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
            options={'verbose_name': 'Transação', 'verbose_name_plural': 'Transações', 'ordering': ['-due_date']},
        ),
        migrations.CreateModel(
            name='HistoricalTransaction',
            fields=[
                ('id', models.BigIntegerField(auto_created=True, blank=True, db_index=True)),
                ('type', models.CharField(max_length=10)),
                ('category', models.CharField(max_length=30)),
                ('description', models.TextField()),
                ('value', models.DecimalField(decimal_places=2, max_digits=15)),
                ('due_date', models.DateField()),
                ('status', models.CharField(default='pendente', max_length=15)),
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
            options={'verbose_name': 'historical transaction', 'ordering': ['-history_date', '-history_id'], 'get_latest_by': ('history_date', 'history_id')},
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
    ]
