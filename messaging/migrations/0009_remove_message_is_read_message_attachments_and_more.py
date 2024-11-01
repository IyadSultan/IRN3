# Generated by Django 5.1.2 on 2024-10-31 09:49

import messaging.models
import messaging.validators
import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("messaging", "0008_remove_message_attachments_message_is_read_and_more"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="message",
            name="is_read",
        ),
        migrations.AddField(
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
                blank=True, default=messaging.models.get_default_respond_by, null=True
            ),
        ),
        migrations.AlterField(
            model_name="message",
            name="thread_id",
            field=models.UUIDField(default=uuid.uuid4, editable=False),
        ),
        migrations.DeleteModel(
            name="MessageAttachment",
        ),
    ]
