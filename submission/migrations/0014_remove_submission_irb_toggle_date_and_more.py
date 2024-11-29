# Generated by Django 5.1.2 on 2024-11-29 19:37

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("forms_builder", "0004_alter_studytype_options_and_more"),
        (
            "submission",
            "0013_submission_irb_toggle_date_submission_irb_toggled_by_and_more",
        ),
    ]

    operations = [
        migrations.RemoveField(
            model_name="submission",
            name="irb_toggle_date",
        ),
        migrations.RemoveField(
            model_name="submission",
            name="irb_toggled_by",
        ),
        migrations.RemoveField(
            model_name="submission",
            name="rc_toggle_date",
        ),
        migrations.RemoveField(
            model_name="submission",
            name="rc_toggled_by",
        ),
        migrations.RemoveField(
            model_name="submission",
            name="show_in_irb",
        ),
        migrations.RemoveField(
            model_name="submission",
            name="show_in_rc",
        ),
        migrations.AlterField(
            model_name="submission",
            name="study_type",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="forms_builder.studytype",
            ),
        ),
    ]
