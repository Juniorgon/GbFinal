import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('tasks', '0003_fix_historicaltask_description'),
    ]

    operations = [
        migrations.CreateModel(
            name='PersonalAppointment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200, verbose_name='Titulo')),
                ('description', models.TextField(blank=True, default='', verbose_name='Descricao')),
                ('date', models.DateField(verbose_name='Data')),
                ('start_time', models.TimeField(blank=True, null=True, verbose_name='Horario Inicial')),
                ('end_time', models.TimeField(blank=True, null=True, verbose_name='Horario Final')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('owner', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='personal_appointments',
                    to=settings.AUTH_USER_MODEL,
                    verbose_name='Usuario',
                )),
            ],
            options={
                'verbose_name': 'Compromisso pessoal',
                'verbose_name_plural': 'Compromissos pessoais',
                'ordering': ['date', 'start_time', 'title'],
            },
        ),
    ]
