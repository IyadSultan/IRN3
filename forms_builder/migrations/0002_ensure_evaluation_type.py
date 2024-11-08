from django.db import migrations

def create_evaluation_type(apps, schema_editor):
    StudyType = apps.get_model('forms_builder', 'StudyType')
    
    # Create Evaluation type if it doesn't exist
    StudyType.objects.get_or_create(
        name='Evaluation',
        defaults={
            'description': 'Forms for evaluation reviews',
            'requires_irb': True,
            'requires_research_council': True,
            'requires_aharpp': True
        }
    )

def reverse_migration(apps, schema_editor):
    StudyType = apps.get_model('forms_builder', 'StudyType')
    StudyType.objects.filter(name='Evaluation').delete()

class Migration(migrations.Migration):
    dependencies = [
        ('forms_builder', '0001_initial'),  # Make sure this matches your initial migration name
    ]

    operations = [
        migrations.RunPython(create_evaluation_type, reverse_migration),
    ] 