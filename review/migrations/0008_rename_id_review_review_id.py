# Generated by Django 5.1.2 on 2024-11-07 21:18

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("review", "0007_alter_review_id"),
    ]

    operations = [
        migrations.RenameField(
            model_name="review",
            old_name="id",
            new_name="review_id",
        ),
    ]
