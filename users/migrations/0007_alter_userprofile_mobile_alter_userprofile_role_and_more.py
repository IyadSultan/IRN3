# Generated by Django 5.1.2 on 2024-11-08 23:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0006_alter_document_options_alter_group_options_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="userprofile",
            name="mobile",
            field=models.CharField(max_length=20),
        ),
        migrations.AlterField(
            model_name="userprofile",
            name="role",
            field=models.CharField(
                blank=True,
                choices=[
                    ("KHCC investigator", "KHCC investigator"),
                    ("Non-KHCC investigator", "Non-KHCC investigator"),
                    (
                        "Research Assistant/Coordinator",
                        "Research Assistant/Coordinator",
                    ),
                    ("OSAR head", "OSAR head"),
                    ("OSAR", "OSAR"),
                    ("IRB chair", "IRB chair"),
                    ("RC coordinator", "RC coordinator"),
                    ("IRB member", "IRB member"),
                    ("RC chair", "RC chair"),
                    ("RC member", "RC member"),
                    ("AHARPP Head", "AHARPP Head"),
                    ("System administrator", "System administrator"),
                    ("CEO", "CEO"),
                    ("CMO", "CMO"),
                    ("AIDI Head", "AIDI Head"),
                    ("Grant Management Officer", "Grant Management Officer"),
                ],
                max_length=50,
                null=True,
            ),
        ),
        migrations.AlterField(
            model_name="userprofile",
            name="title",
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
