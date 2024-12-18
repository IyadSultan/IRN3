# Generated by Django 5.1.2 on 2024-11-09 21:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("submission", "0007_alter_submission_irb_number"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="versionhistory",
            options={"ordering": ["-version"]},
        ),
        migrations.AlterField(
            model_name="versionhistory",
            name="date",
            field=models.DateTimeField(auto_now_add=True),
        ),
        migrations.AlterField(
            model_name="versionhistory",
            name="status",
            field=models.CharField(max_length=20),
        ),
        migrations.AlterField(
            model_name="versionhistory",
            name="version",
            field=models.IntegerField(),
        ),
        migrations.AlterUniqueTogether(
            name="versionhistory",
            unique_together={("submission", "version")},
        ),
    ]
