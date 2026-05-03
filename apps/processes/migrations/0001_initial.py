import django.db.models.deletion
import simple_history.models
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('branches', '0001_initial'),
        ('clients', '0001_initial'),
        ('lawyers', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Process',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('number', models.CharField(blank=True, max_length=50, verbose_name='Número do Processo')),
                ('type', models.CharField(choices=[
                    ('civil','Cível'),('trabalhista','Trabalhista'),('criminal','Criminal'),
                    ('familia','Família'),('previdenciario','Previdenciário'),('tributario','Tributário'),
                    ('empresarial','Empresarial'),('administrativo','Administrativo'),('outro','Outro'),
                ], max_length=20, verbose_name='Tipo')),
                ('status', models.CharField(choices=[
                    ('andamento','Em Andamento'),('concluido','Concluído'),
                    ('suspenso','Suspenso'),('arquivado','Arquivado'),
                ], default='andamento', max_length=15, verbose_name='Status')),
                ('client_position', models.CharField(choices=[
                    ('autor','Credor (Autor)'),('reu','Devedor (Réu)'),
                    ('terceiro','Terceiro Interessado'),('outro','Outro'),
                ], default='autor', max_length=10, verbose_name='Posição do Cliente')),
                ('value', models.DecimalField(decimal_places=2, default=0, max_digits=15, verbose_name='Valor da Causa')),
                ('description', models.TextField(blank=True, verbose_name='Descrição')),
                ('court', models.CharField(blank=True, max_length=200, verbose_name='Vara/Tribunal')),
                ('judge', models.CharField(blank=True, max_length=100, verbose_name='Juiz')),
                ('opposing_party', models.CharField(blank=True, max_length=200, verbose_name='Parte Contrária')),
                ('notes', models.TextField(blank=True, verbose_name='Observações')),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('branch', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='processes', to='branches.branch')),
                ('client', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='processes', to='clients.client', verbose_name='Cliente')),
                ('lawyer', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='processes', to='lawyers.lawyer', verbose_name='Advogado')),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
            options={'verbose_name': 'Processo', 'verbose_name_plural': 'Processos', 'ordering': ['-created_at']},
        ),
        migrations.CreateModel(
            name='ProcessUpdate',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('date', models.DateField(verbose_name='Data')),
                ('title', models.CharField(max_length=200, verbose_name='Título')),
                ('description', models.TextField(verbose_name='Descrição')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('process', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='updates', to='processes.process')),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
            options={'verbose_name': 'Andamento', 'verbose_name_plural': 'Andamentos', 'ordering': ['-date']},
        ),
        migrations.CreateModel(
            name='HistoricalProcess',
            fields=[
                ('id', models.BigIntegerField(auto_created=True, blank=True, db_index=True)),
                ('number', models.CharField(blank=True, max_length=50)),
                ('type', models.CharField(max_length=20)),
                ('status', models.CharField(default='andamento', max_length=15)),
                ('value', models.DecimalField(decimal_places=2, default=0, max_digits=15)),
                ('is_active', models.BooleanField(default=True)),
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
            options={'verbose_name': 'historical process', 'ordering': ['-history_date', '-history_id'], 'get_latest_by': ('history_date', 'history_id')},
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
    ]
