# utils/validation.py

from django import forms
import json

def get_validation_errors(submission):
    """
    Validate all forms in the submission and return any errors.
    """
    validation_errors = {}
    
    # Get all forms for this study type
    for dynamic_form in submission.study_type.forms.order_by('order'):
        django_form_class = generate_django_form(dynamic_form)
        entries = FormDataEntry.objects.filter(
            submission=submission, 
            form=dynamic_form, 
            version=submission.version
        )
        saved_data = {
            f'form_{dynamic_form.id}-{entry.field_name}': entry.value
            for entry in entries
        }
        
        form_instance = django_form_class(data=saved_data, prefix=f'form_{dynamic_form.id}')
        is_valid = True
        errors = {}
        
        for field_name, field in form_instance.fields.items():
            field_key = f'form_{dynamic_form.id}-{field_name}'
            field_value = saved_data.get(field_key)
            
            if isinstance(field, forms.MultipleChoiceField):
                try:
                    if field.required and (not field_value or field_value == '[]'):
                        is_valid = False
                        errors[field_name] = ['This field is required']
                except json.JSONDecodeError:
                    is_valid = False
                    errors[field_name] = ['Invalid value']
            else:
                if field.required and not field_value:
                    is_valid = False
                    errors[field_name] = ['This field is required']

        if not is_valid:
            validation_errors[dynamic_form.name] = errors

    return validation_errors

def check_certifications(user_profile):
    """
    Check if a user's certifications are valid.
    """
    issues = []
    
    if not user_profile.has_valid_gcp:
        issues.append('GCP Certificate missing or expired')
    if not user_profile.has_cv:
        issues.append('CV missing')
    if user_profile.role == 'KHCC investigator':
        if not user_profile.has_qrc:
            issues.append('QRC Certificate missing')
        if not user_profile.has_ctc:
            issues.append('CTC Certificate missing')
    elif user_profile.role == 'Research Assistant/Coordinator':
        if not user_profile.has_ctc:
            issues.append('CTC Certificate missing')
            
    return issues

def check_team_certifications(submission):
    """
    Check certifications for the entire research team.
    """
    certification_issues = {}
    
    # Check PI certifications
    pi_issues = check_certifications(submission.primary_investigator.userprofile)
    if pi_issues:
        certification_issues['Primary Investigator'] = {
            'name': submission.primary_investigator.get_full_name(),
            'issues': pi_issues
        }
    
    # Check Co-Investigator certifications
    for coinv in submission.coinvestigators.all():
        coinv_issues = check_certifications(coinv.user.userprofile)
        if coinv_issues:
            certification_issues[f'Co-Investigator'] = {
                'name': coinv.user.get_full_name(),
                'issues': coinv_issues
            }
    
    # Check Research Assistant certifications
    for ra in submission.research_assistants.all():
        ra_issues = check_certifications(ra.user.userprofile)
        if ra_issues:
            certification_issues[f'Research Assistant'] = {
                'name': ra.user.get_full_name(),
                'issues': ra_issues
            }
    
    return certification_issues