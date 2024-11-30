# Generated by Django 5.1.3 on 2024-11-30 14:06

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("review", "0015_delete_notepadentry"),
        ("submission", "0014_submission_show_in_irb_submission_show_in_rc"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="NotepadEntry",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "notepad_type",
                    models.CharField(
                        choices=[("OSAR", "OSAR"), ("IRB", "IRB"), ("RC", "RC")],
                        max_length=10,
                    ),
                ),
                ("text", models.TextField()),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "created_by",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "submission",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="notepad_entries",
                        to="submission.submission",
                    ),
                ),
            ],
            options={
                "verbose_name": "Notepad Entry",
                "verbose_name_plural": "Notepad Entries",
                "ordering": ["-created_at"],
            },
        ),
    ]