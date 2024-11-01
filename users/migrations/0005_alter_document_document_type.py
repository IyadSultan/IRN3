# Generated by Django 5.1.2 on 2024-10-30 21:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0004_remove_userprofile_cv"),
    ]

    operations = [
        migrations.AlterField(
            model_name="document",
            name="document_type",
            field=models.CharField(
                choices=[
                    ("GCP", "Good Clinical Practice Certificate"),
                    ("QRC", "Qualitative Record Certificate"),
                    ("CTC", "Consent Training Certificate"),
                    ("Other", "Other"),
                ],
                max_length=20,
            ),
        ),
    ]
