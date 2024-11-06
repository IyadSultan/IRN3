# Generated by Django 5.1.2 on 2024-11-06 02:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        (
            "forms_builder",
            "0002_alter_dynamicform_options_alter_formfield_options_and_more",
        ),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="dynamicform",
            options={
                "ordering": ["order", "name"],
                "verbose_name": "Dynamic Form",
                "verbose_name_plural": "Dynamic Forms",
            },
        ),
        migrations.AlterField(
            model_name="dynamicform",
            name="requested_per_investigator",
            field=models.BooleanField(
                default=False,
                help_text="If checked, one form will be required per investigator",
            ),
        ),
        migrations.AlterField(
            model_name="dynamicform",
            name="version",
            field=models.PositiveIntegerField(default=1),
        ),
    ]
