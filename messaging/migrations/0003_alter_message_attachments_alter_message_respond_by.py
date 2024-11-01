# Generated by Django 5.1.2 on 2024-10-27 00:37

import datetime
import messaging.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("messaging", "0002_alter_message_respond_by"),
    ]

    operations = [
        migrations.AlterField(
            model_name="message",
            name="attachments",
            field=models.FileField(
                blank=True,
                null=True,
                upload_to="attachments/",
                validators=[messaging.validators.validate_file_size],
            ),
        ),
        migrations.AlterField(
            model_name="message",
            name="respond_by",
            field=models.DateTimeField(
                blank=True,
                default=datetime.datetime(
                    2024, 11, 10, 0, 37, 42, 236935, tzinfo=datetime.timezone.utc
                ),
                null=True,
            ),
        ),
    ]
