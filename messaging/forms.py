# messaging/forms.py

from django import forms
from django.db.models import Q
from django.contrib.auth import get_user_model
from submission.models import Submission
from .models import Message, MessageAttachment
from .validators import validate_file_size, validate_file_extension

User = get_user_model()

class MessageForm(forms.ModelForm):
    recipients = forms.ModelMultipleChoiceField(
        queryset=User.objects.filter(is_active=True),
        widget=forms.SelectMultiple(attrs={
            'class': 'form-control select2',
            'data-placeholder': 'Select recipients...'
        })
    )

    cc = forms.ModelMultipleChoiceField(
        queryset=User.objects.filter(is_active=True),
        required=False,
        widget=forms.SelectMultiple(attrs={
            'class': 'form-control select2',
            'data-placeholder': 'Select CC recipients...'
        })
    )

    bcc = forms.ModelMultipleChoiceField(
        queryset=User.objects.filter(is_active=True),
        required=False,
        widget=forms.SelectMultiple(attrs={
            'class': 'form-control select2',
            'data-placeholder': 'Select BCC recipients...'
        })
    )

    subject = forms.CharField(
        max_length=255,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter subject...'
        })
    )

    body = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 5,
            'placeholder': 'Type your message here...'
        })
    )

    related_submission = forms.ModelChoiceField(
        queryset=Submission.objects.all(),
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-control select2',
            'data-placeholder': 'Link to a submission...'
        })
    )

    attachment = forms.FileField(
        required=False,
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': '.pdf,.doc,.docx,.txt,.xls,.xlsx,.jpg,.jpeg,.png'
        }),
        validators=[validate_file_size, validate_file_extension]
    )

    class Meta:
        model = Message
        fields = ['subject', 'body', 'recipients', 'cc', 'bcc', 'related_submission']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        initial_recipients = kwargs.pop('initial_recipients', None)
        initial_submission = kwargs.pop('initial_submission', None)
        reply_to = kwargs.pop('reply_to', None)
        super().__init__(*args, **kwargs)

        if user:
            # Exclude current user from recipients
            excluded_user_queryset = User.objects.exclude(id=user.id).filter(is_active=True)
            self.fields['recipients'].queryset = excluded_user_queryset
            self.fields['cc'].queryset = excluded_user_queryset
            self.fields['bcc'].queryset = excluded_user_queryset

            # Update related_submission queryset with accessible submissions
            if user.is_authenticated:
                accessible_submissions = Submission.objects.filter(
                    Q(primary_investigator=user) |
                    Q(coinvestigators__user=user) |
                    Q(research_assistants__user=user)
                ).distinct()
                self.fields['related_submission'].queryset = accessible_submissions

        # Handle initial data
        if initial_recipients:
            self.fields['recipients'].initial = initial_recipients

        if initial_submission:
            self.fields['related_submission'].initial = initial_submission

        # Handle reply-to case
        if reply_to:
            if not self.initial.get('subject', '').startswith('Re:'):
                self.initial['subject'] = 'Re: ' + reply_to.subject
            
            self.initial['related_submission'] = reply_to.related_submission
            
            # Create the reply body parts separately
            date_str = reply_to.sent_at.strftime('%Y-%m-%d %H:%M')
            sender_name = reply_to.sender.get_full_name()
            
            # Create the quoted lines
            quoted_lines = []
            for line in reply_to.body.splitlines():
                quoted_lines.append('> ' + line)
            
            # Combine all parts
            self.initial['body'] = '\n\nOn {}, {} wrote:\n{}'.format(
                date_str,
                sender_name,
                '\n'.join(quoted_lines)
            )

    def clean(self):
        cleaned_data = super().clean()
        recipients = cleaned_data.get('recipients', [])
        cc = cleaned_data.get('cc', [])
        bcc = cleaned_data.get('bcc', [])

        if not recipients:
            self.add_error('recipients', 'At least one recipient is required.')

        # Check for duplicates across all recipient fields
        all_recipients = set()
        for recipient in recipients:
            if recipient.id in all_recipients:
                self.add_error('recipients', 'Duplicate recipient found.')
            all_recipients.add(recipient.id)

        for cc_recipient in cc:
            if cc_recipient.id in all_recipients:
                self.add_error('cc', 'Recipient already included in To field.')
            all_recipients.add(cc_recipient.id)

        for bcc_recipient in bcc:
            if bcc_recipient.id in all_recipients:
                self.add_error('bcc', 'Recipient already included in To or CC field.')
            all_recipients.add(bcc_recipient.id)

        return cleaned_data

    def clean_attachment(self):
        """
        Validate single file attachment
        """
        attachment = self.cleaned_data.get('attachment')
        if attachment:
            if attachment.size > 10 * 1024 * 1024:  # 10MB limit
                raise forms.ValidationError("File is too large. Maximum size is 10MB.")
            
            ext = attachment.name.split('.')[-1].lower()
            if ext not in ['pdf', 'doc', 'docx', 'txt', 'xls', 'xlsx', 'jpg', 'jpeg', 'png']:
                raise forms.ValidationError(f"File type .{ext} is not allowed.")
        
        return attachment

    def save(self, commit=True):
        message = super().save(commit=False)
        
        if commit:
            message.save()
            self.save_m2m()
            
            # Handle attachment
            if self.cleaned_data.get('attachment'):
                MessageAttachment.objects.create(
                    message=message,
                    file=self.cleaned_data['attachment'],
                    filename=self.cleaned_data['attachment'].name
                )
                
        return message
    
class SearchForm(forms.Form):
    q = forms.CharField(label='Search', max_length=100)
