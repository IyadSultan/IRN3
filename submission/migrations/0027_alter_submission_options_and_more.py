# Generated by Django 5.1.3 on 2024-12-05 17:33

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("forms_builder", "0003_merge_20241108_1706"),
        ("submission", "0026_formdataentry_study_action"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="submission",
            options={"ordering": ["-date_created"]},
        ),
        migrations.AddIndex(
            model_name="submission",
            index=models.Index(fields=["status"], name="submission__status_832d62_idx"),
        ),
        migrations.AddIndex(
            model_name="submission",
            index=models.Index(
                fields=["khcc_number"], name="submission__khcc_nu_653cf0_idx"
            ),
        ),
        migrations.AddIndex(
            model_name="submission",
            index=models.Index(
                fields=["primary_investigator"], name="submission__primary_7bae28_idx"
            ),
        ),
        migrations.AddIndex(
            model_name="submission",
            index=models.Index(
                fields=["is_archived"], name="submission__is_arch_0823ea_idx"
            ),
        ),
    ]