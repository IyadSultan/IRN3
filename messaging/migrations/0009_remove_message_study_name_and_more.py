# Generated by Django 5.1.2 on 2024-11-09 18:15

import messaging.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("messaging", "0008_notificationstatus"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="message",
            name="study_name",
        ),
        migrations.AlterField(
            model_name="messageattachment",
            name="file",
            field=models.FileField(
                upload_to="message_attachments/",
                validators=[
                    messaging.validators.validate_file_size,
                    messaging.validators.validate_file_extension,
                ],
            ),
        ),
    ]
