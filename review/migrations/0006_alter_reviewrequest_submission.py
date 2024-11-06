# Generated by Django 5.1.2 on 2024-11-06 01:29

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("review", "0005_reviewrequest_can_forward_and_more"),
        ("submission", "0005_statuschoice_alter_submission_status_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="reviewrequest",
            name="submission",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="review_requests",
                to="submission.submission",
            ),
        ),
    ]
