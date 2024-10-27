# Django Messaging App

A standalone messaging app for Django with features similar to Gmail.

## Features

- Unread messages in bold
- Threaded conversations
- Sent and archived messages
- Optional fields for study name and respond by date
- Attachments up to 10 MB
- Email notifications
- Dynamic message icon
- Modern UI with night mode
- Forms for viewing and sending messages
- Autocomplete for recipients
- Search functionality
- Hashtags and comments
- Standalone app with integration instructions
- Testing files included

## Installation

1. Add `'messaging'` to `INSTALLED_APPS` in `settings.py`.
2. Include messaging URLs in your project's `urls.py`:

```python
path('messaging/', include('messaging.urls', namespace='messaging')),
