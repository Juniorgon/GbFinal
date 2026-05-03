from django.db import migrations, models


def set_nova_prata_as_headquarters(apps, schema_editor):
    Branch = apps.get_model('branches', 'Branch')
    Branch.objects.all().update(is_headquarters=False)
    Branch.objects.filter(name='Nova Prata').update(is_headquarters=True)


class Migration(migrations.Migration):

    dependencies = [
        ('branches', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='branch',
            name='is_headquarters',
            field=models.BooleanField(default=False, verbose_name='Sede Principal'),
        ),
        migrations.RunPython(set_nova_prata_as_headquarters, migrations.RunPython.noop),
    ]
