# Media files configuration
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Make sure you have these settings for file uploads
FILE_UPLOAD_HANDLERS = [
    'django.core.files.uploadhandler.MemoryFileUploadHandler',
    'django.core.files.uploadhandler.TemporaryFileUploadHandler',
]

# Optional: Set maximum upload size if needed
# DATA_UPLOAD_MAX_MEMORY_SIZE = 5242880  # 5MB 