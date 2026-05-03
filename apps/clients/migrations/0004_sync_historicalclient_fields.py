from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('clients', '0003_remove_client_phone2'),
    ]

    operations = [
        migrations.RunSQL(
            sql="""
                ALTER TABLE clients_historicalclient
                    ADD COLUMN IF NOT EXISTS nationality varchar(50) NOT NULL DEFAULT 'Brasileira',
                    ADD COLUMN IF NOT EXISTS marital_status varchar(50) NOT NULL DEFAULT '',
                    ADD COLUMN IF NOT EXISTS profession varchar(100) NOT NULL DEFAULT '',
                    ADD COLUMN IF NOT EXISTS birth_date date NULL,
                    ADD COLUMN IF NOT EXISTS email varchar(254) NOT NULL DEFAULT '',
                    ADD COLUMN IF NOT EXISTS street varchar(200) NOT NULL DEFAULT '',
                    ADD COLUMN IF NOT EXISTS number varchar(10) NOT NULL DEFAULT '',
                    ADD COLUMN IF NOT EXISTS complement varchar(100) NOT NULL DEFAULT '',
                    ADD COLUMN IF NOT EXISTS district varchar(100) NOT NULL DEFAULT '',
                    ADD COLUMN IF NOT EXISTS zipcode varchar(10) NOT NULL DEFAULT '',
                    ADD COLUMN IF NOT EXISTS notes text NOT NULL DEFAULT '';
            """,
            reverse_sql="""
                ALTER TABLE clients_historicalclient
                    DROP COLUMN IF EXISTS nationality,
                    DROP COLUMN IF EXISTS marital_status,
                    DROP COLUMN IF EXISTS profession,
                    DROP COLUMN IF EXISTS birth_date,
                    DROP COLUMN IF EXISTS email,
                    DROP COLUMN IF EXISTS street,
                    DROP COLUMN IF EXISTS number,
                    DROP COLUMN IF EXISTS complement,
                    DROP COLUMN IF EXISTS district,
                    DROP COLUMN IF EXISTS zipcode,
                    DROP COLUMN IF EXISTS notes;
            """,
        ),
    ]
