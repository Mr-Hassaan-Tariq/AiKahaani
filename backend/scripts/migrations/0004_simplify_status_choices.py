# Generated migration for simplifying status choices

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('scripts', '0003_make_script_optional_in_outline'),
    ]

    operations = [
        migrations.AlterField(
            model_name='scriptoutline',
            name='status',
            field=models.CharField(
                choices=[
                    ('draft', 'Draft'),
                    ('generated', 'Generated'),
                    ('saved', 'Saved'),
                ],
                default='draft',
                max_length=20
            ),
        ),
        migrations.AlterField(
            model_name='fullscript',
            name='status',
            field=models.CharField(
                choices=[
                    ('draft', 'Draft'),
                    ('generated', 'Generated'),
                    ('saved', 'Saved'),
                ],
                default='draft',
                max_length=20
            ),
        ),
    ]
