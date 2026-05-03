import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('accounts', '0001_initial'),
        ('branches', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Lawyer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200, verbose_name='Nome Completo')),
                ('email', models.EmailField(verbose_name='Email')),
                ('oab_number', models.CharField(max_length=20, verbose_name='Número OAB')),
                ('oab_state', models.CharField(
                    choices=[('AC','AC'),('AL','AL'),('AP','AP'),('AM','AM'),('BA','BA'),('CE','CE'),
                             ('DF','DF'),('ES','ES'),('GO','GO'),('MA','MA'),('MT','MT'),('MS','MS'),
                             ('MG','MG'),('PA','PA'),('PB','PB'),('PR','PR'),('PE','PE'),('PI','PI'),
                             ('RJ','RJ'),('RN','RN'),('RS','RS'),('RO','RO'),('RR','RR'),('SC','SC'),
                             ('SP','SP'),('SE','SE'),('TO','TO')],
                    default='RS', max_length=2, verbose_name='Estado OAB'
                )),
                ('phone', models.CharField(blank=True, max_length=20, verbose_name='Telefone')),
                ('specialization', models.CharField(blank=True, max_length=200, verbose_name='Especialização')),
                ('is_active', models.BooleanField(default=True, verbose_name='Ativo')),
                ('can_access_financial', models.BooleanField(default=False, verbose_name='Acesso Financeiro')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('accessible_branches', models.ManyToManyField(
                    blank=True, related_name='accessible_lawyers',
                    to='branches.branch', verbose_name='Filiais com Acesso'
                )),
                ('branch', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='lawyers', to='branches.branch'
                )),
                ('user', models.OneToOneField(
                    blank=True, null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name='lawyer_profile', to='accounts.customuser'
                )),
            ],
            options={
                'verbose_name': 'Advogado',
                'verbose_name_plural': 'Advogados',
                'ordering': ['name'],
            },
        ),
    ]
