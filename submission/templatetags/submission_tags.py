from django import template

register = template.Library()

@register.filter
def next(value, arg):
    """
    Returns the next item from a list
    """
    try:
        return value[int(arg) + 1]
    except:
        return None

@register.filter
def attr(obj, attr):
    """
    Gets an attribute of an object dynamically
    """
    try:
        return getattr(obj, attr)
    except:
        return None
