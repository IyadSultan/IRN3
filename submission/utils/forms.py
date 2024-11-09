# submission/utils/forms.py

from django import forms
import json


def generate_django_form(dynamic_form):
    """
    Dynamically generate a Django form class based on a DynamicForm instance.
    """
    class DynamicModelForm(forms.Form):
        pass

    fields = {}
    for field in dynamic_form.fields.all():
        label = f"{field.displayed_name}{'*' if field.required else ''}"
        field_attrs = {
            'required': field.required,
            'label': label,
            'help_text': field.help_text,
            'initial': field.default_value,
        }
        widget_attrs = {'class': 'form-control'}

        if field.field_type == 'text':
            fields[field.name] = forms.CharField(
                max_length=field.max_length or 255,
                widget=forms.TextInput(attrs=widget_attrs),
                **field_attrs,
            )
        elif field.field_type == 'email':
            fields[field.name] = forms.EmailField(
                max_length=field.max_length or 255,
                widget=forms.EmailInput(attrs=widget_attrs),
                **field_attrs,
            )
        elif field.field_type == 'tel':
            fields[field.name] = forms.CharField(
                max_length=field.max_length or 15,
                widget=forms.TextInput(attrs={'class': 'form-control', 'type': 'tel'}),
                **field_attrs,
            )
        elif field.field_type == 'textarea':
            fields[field.name] = forms.CharField(
                max_length=field.max_length or 500,
                widget=forms.Textarea(attrs=widget_attrs),
                **field_attrs,
            )
        elif field.field_type == 'checkbox':
            choices = [
                (choice.strip(), choice.strip())
                for choice in field.choices.split(',')
                if choice.strip()
            ]
            fields[field.name] = forms.MultipleChoiceField(
                choices=choices,
                widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
                required=field.required,
            )
        elif field.field_type == 'radio':
            choices = [
                (choice.strip(), choice.strip())
                for choice in field.choices.split(',')
                if choice.strip()
            ]
            fields[field.name] = forms.ChoiceField(
                choices=choices,
                widget=forms.RadioSelect(attrs={'class': 'form-check-input'}),
                **field_attrs,
            )
        elif field.field_type == 'select':
            choices = [
                (choice.strip(), choice.strip())
                for choice in field.choices.split(',')
                if choice.strip()
            ]
            fields[field.name] = forms.ChoiceField(
                choices=[('', '-- Select --')] + choices,
                widget=forms.Select(attrs=widget_attrs),
                **field_attrs,
            )
        elif field.field_type == 'number':
            fields[field.name] = forms.IntegerField(
                widget=forms.NumberInput(attrs=widget_attrs), **field_attrs
            )
        elif field.field_type == 'date':
            fields[field.name] = forms.DateField(
                widget=forms.DateInput(attrs={'type': 'date', **widget_attrs}),
                **field_attrs,
            )
        # Add other field types as necessary

    DynamicModelForm.base_fields = fields
    return DynamicModelForm
