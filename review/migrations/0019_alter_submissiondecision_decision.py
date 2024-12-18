# Generated by Django 5.1.3 on 2024-12-06 12:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("review", "0018_submissiondecision"),
    ]

    operations = [
        migrations.AlterField(
            model_name="submissiondecision",
            name="decision",
            field=models.CharField(
                choices=[
                    ("revision_requested", "Revision Requested"),
                    ("rejected", "Rejected"),
                    ("accepted", "Accepted"),
                    ("provisional_approval", "Provisional Approval"),
                    ("suspended", "Suspended"),
                ],
                max_length=20,
            ),
        ),
    ]
