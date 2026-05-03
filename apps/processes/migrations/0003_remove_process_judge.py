from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('processes', '0002_process_custom_type'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='process',
            name='judge',
        ),
    ]
