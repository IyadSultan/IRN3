# Generated by Django 5.1.2 on 2024-11-07 22:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("review", "0008_rename_id_review_review_id"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="review",
            options={"ordering": ["-date_submitted"]},
        ),
        migrations.AddField(
            model_name="review",
            name="is_completed",
            field=models.BooleanField(default=False),
        ),
    ]
