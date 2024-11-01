# Generated by Django 5.1.2 on 2024-10-27 23:57

import messaging.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("messaging", "0004_alter_message_respond_by"),
    ]

    operations = [
        migrations.AlterField(
            model_name="message",
            name="respond_by",
            field=models.DateTimeField(
                blank=True, default=messaging.models.get_default_respond_by, null=True
            ),
        ),
    ]
