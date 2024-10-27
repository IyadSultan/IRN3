from django import template
from django.template.defaultfilters import stringfilter

register = template.Library()

@register.filter
@stringfilter
def get_read_status(message, user):
    try:
        return message.read_statuses.get(user=user).is_read
    except:
        return False

# Define your custom template tags and filters here
@register.filter
def example_filter(value):
    return value

@register.simple_tag
def example_tag():
    return "This is an example tag"

