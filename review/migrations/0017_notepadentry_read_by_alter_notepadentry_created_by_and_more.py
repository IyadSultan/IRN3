# Generated by Django 5.1.3 on 2024-12-02 20:17

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("review", "0016_notepadentry"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name="notepadentry",
            name="read_by",
            field=models.ManyToManyField(
                blank=True, related_name="read_notes", to=settings.AUTH_USER_MODEL
            ),
        ),
        migrations.AlterField(
            model_name="notepadentry",
            name="created_by",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="created_notes",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AlterModelTable(
            name="notepadentry",
            table="review_notepad_entry",
        ),
    ]
