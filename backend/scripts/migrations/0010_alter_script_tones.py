# Generated manually for multiple tones support

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('scripts', '0009_script_user'),
    ]

    operations = [
        # First, remove the old tone ForeignKey field
        migrations.RemoveField(
            model_name='script',
            name='tone',
        ),
        # Then add the new tones ManyToManyField
        migrations.AddField(
            model_name='script',
            name='tones',
            field=models.ManyToManyField(
                help_text='The tones/vibes for this script',
                related_name='scripts',
                to='scripts.tone'
            ),
        ),
    ]
