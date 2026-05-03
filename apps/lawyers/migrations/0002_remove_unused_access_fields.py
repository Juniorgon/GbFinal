from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('lawyers', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='lawyer',
            name='accessible_branches',
        ),
        migrations.RemoveField(
            model_name='lawyer',
            name='can_access_financial',
        ),
    ]
