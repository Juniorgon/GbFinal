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
        ('processes', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Task',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('title', models.CharField(max_length=200, verbose_name='Título')),
                ('type', models.CharField(choices=[
                    ('audiencia','Audiência'),('prazo','Prazo'),('reuniao','Reunião'),
                    ('protocolo','Protocolo'),('ligacao','Ligação'),('outro','Outro'),
                ], default='outro', max_length=20, verbose_name='Tipo')),
                ('description', models.TextField(blank=True, verbose_name='Descrição')),
                ('due_date', models.DateField(verbose_name='Data de Vencimento')),
                ('priority', models.CharField(choices=[
                    ('alta','Alta'),('media','Média'),('baixa','Baixa'),
                ], default='media', max_length=6, verbose_name='Prioridade')),
                ('status', models.CharField(choices=[
                    ('pendente','Pendente'),('andamento','Em Andamento'),
                    ('aguardando','Aguardando Validação'),
                    ('concluida','Concluída'),('cancelada','Cancelada'),
                ], default='pendente', max_length=12, verbose_name='Status')),
                ('completion_note', models.TextField(blank=True, verbose_name='Nota de Conclusão')),
                ('completed_at', models.DateTimeField(blank=True, null=True, verbose_name='Data de Conclusão')),
                ('validated_at', models.DateTimeField(blank=True, null=True, verbose_name='Data de Validação')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('branch', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tasks', to='branches.branch')),
                ('assigned_to', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='tasks', to='lawyers.lawyer', verbose_name='Advogado Responsável')),
                ('client', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='tasks', to='clients.client', verbose_name='Cliente')),
                ('process', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='tasks', to='processes.process', verbose_name='Processo')),
                ('completed_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='tasks_completed', to=settings.AUTH_USER_MODEL, verbose_name='Concluída por')),
                ('validated_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='tasks_validated', to=settings.AUTH_USER_MODEL, verbose_name='Validada por')),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='tasks_created', to=settings.AUTH_USER_MODEL)),
            ],
            options={'verbose_name': 'Tarefa', 'verbose_name_plural': 'Tarefas', 'ordering': ['due_date', '-priority']},
        ),
        migrations.CreateModel(
            name='HistoricalTask',
            fields=[
                ('id', models.BigIntegerField(auto_created=True, blank=True, db_index=True)),
                ('title', models.CharField(max_length=200)),
                ('type', models.CharField(default='outro', max_length=20)),
                ('due_date', models.DateField()),
                ('priority', models.CharField(default='media', max_length=6)),
                ('status', models.CharField(default='pendente', max_length=12)),
                ('created_at', models.DateTimeField(blank=True, editable=False)),
                ('updated_at', models.DateTimeField(blank=True, editable=False)),
                ('history_id', models.AutoField(primary_key=True, serialize=False)),
                ('history_date', models.DateTimeField(db_index=True)),
                ('history_change_reason', models.CharField(max_length=100, null=True)),
                ('history_type', models.CharField(choices=[('+','Created'),('~','Changed'),('-','Deleted')], max_length=1)),
                ('branch', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='branches.branch')),
                ('assigned_to', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='lawyers.lawyer')),
                ('created_by', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to=settings.AUTH_USER_MODEL)),
                ('history_user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
            ],
            options={'verbose_name': 'historical task', 'ordering': ['-history_date', '-history_id'], 'get_latest_by': ('history_date', 'history_id')},
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
    ]
