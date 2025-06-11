from django.db import migrations

class Migration(migrations.Migration):

    dependencies = [
        ('formations', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='participation',
            old_name='date',
            new_name='date_inscription',
        ),
    ]
