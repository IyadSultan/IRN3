# messaging/validators.py

from django.core.exceptions import ValidationError
import os

def validate_file_size(value):
    max_kb = 10240  # 10 MB
    if value.size > max_kb * 1024:
        raise ValidationError('Maximum file size is 10 MB.')

def validate_file_extension(value):
    ext = os.path.splitext(value.name)[1].lower()
    valid_extensions = ['.pdf', '.doc', '.docx', '.xls', '.xlsx', '.txt', '.png', '.jpg', '.jpeg']
    if ext not in valid_extensions:
        raise ValidationError('Unsupported file extension.')
