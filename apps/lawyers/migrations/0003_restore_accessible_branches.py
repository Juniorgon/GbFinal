from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('branches', '0002_branch_is_headquarters'),
        ('lawyers', '0002_remove_unused_access_fields'),
    ]

    operations = [
        migrations.AddField(
            model_name='lawyer',
            name='accessible_branches',
            field=models.ManyToManyField(
                blank=True,
                related_name='accessible_lawyers',
                to='branches.branch',
                verbose_name='Filiais com Acesso',
            ),
        ),
    ]
