# Generated by Django 5.1.2 on 2024-10-31 10:16

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0006_systemsettings"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="systemsettings",
            options={
                "verbose_name": "System Settings",
                "verbose_name_plural": "System Settings",
            },
        ),
    ]