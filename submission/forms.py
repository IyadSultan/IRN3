# submission/forms.py

from django import forms
from django.contrib.auth.models import User
from .models import Submission
from dal import autocomplete
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

class SubmissionForm(forms.ModelForm):
    is_primary_investigator = forms.BooleanField(
        required=False, initial=True, label='Are you the primary investigator?'
    )
    primary_investigator = forms.ModelChoiceField(
        queryset=User.objects.all(),
        required=False,
        widget=autocomplete.ModelSelect2(url='submission:user-autocomplete'),
        label='Primary Investigator'
    )

    class Meta:
        model = Submission
        fields = ['title', 'study_type']

class ResearchAssistantForm(forms.Form):
    assistant = forms.ModelChoiceField(
        queryset=User.objects.all(),
        widget=autocomplete.ModelSelect2(url='submission:user-autocomplete'),
        label='Research Assistant'
    )
    can_submit = forms.BooleanField(required=False)
    can_edit = forms.BooleanField(required=False)
    can_view_communications = forms.BooleanField(required=False)

class CoInvestigatorForm(forms.Form):
    investigator = forms.ModelChoiceField(
        queryset=User.objects.all(),
        widget=autocomplete.ModelSelect2(url='submission:user-autocomplete'),
        label='Investigator Name'
    )
    role_in_study = forms.CharField(label='Role in Study')
    can_submit = forms.BooleanField(required=False)
    can_edit = forms.BooleanField(required=False)
    can_view_communications = forms.BooleanField(required=False)

def generate_pdf(response):
    c = canvas.Canvas(response, pagesize=letter)
    c.drawString(100, 750, "Hello World")
    c.save()

# In your view:
from django.http import HttpResponse

def pdf_view(request):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="document.pdf"'
    generate_pdf(response)
    return response
