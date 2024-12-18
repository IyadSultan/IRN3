# Generated by Django 5.1.2 on 2024-11-09 21:43

import submission.models
from django.db import migrations, models
from iRN.constants import get_submission_status_choices


class Migration(migrations.Migration):

    dependencies = [
        ("submission", "0008_alter_versionhistory_options_and_more"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="versionhistory",
            options={},
        ),
        migrations.AlterUniqueTogether(
            name="versionhistory",
            unique_together=set(),
        ),
        migrations.AlterField(
            model_name="versionhistory",
            name="date",
            field=models.DateTimeField(),
        ),
        migrations.AlterField(
            model_name="versionhistory",
            name="status",
            field=models.CharField(
                choices=get_submission_status_choices, max_length=50
            ),
        ),
        migrations.AlterField(
            model_name="versionhistory",
            name="version",
            field=models.PositiveIntegerField(),
        ),
    ]
