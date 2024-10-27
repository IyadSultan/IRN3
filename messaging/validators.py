# messaging/validators.py

from django.core.exceptions import ValidationError

def validate_file_size(value):
    max_kb = 10240  # 10 MB
    if value.size > max_kb * 1024:
        raise ValidationError('Maximum file size is 10 MB')
