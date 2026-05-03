from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('clients', '0002_remove_client_rg'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='client',
            name='phone2',
        ),
    ]
