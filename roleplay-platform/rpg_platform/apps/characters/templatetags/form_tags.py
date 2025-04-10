from django import template
from django.utils.safestring import SafeString

register = template.Library()

@register.filter(name='add_class')
def add_class(field, css_class):
    """Add a CSS class to a form field."""
    if isinstance(field, SafeString):
        return field  # Return as is if it's a SafeString (already rendered)

    if not hasattr(field, 'as_widget'):
        return field

    return field.as_widget(attrs={'class': css_class})

@register.filter(name='attr')
def set_attr(field, attr_name_value):
    """Set an attribute on a form field.

    Usage: {{ field|attr:'required' }} or {{ field|attr:'data-toggle:modal' }}
    """
    if isinstance(field, SafeString):
        return field  # Return as is if it's a SafeString (already rendered)

    if not hasattr(field, 'field'):
        return field

    if ':' in attr_name_value:
        attr_name, attr_value = attr_name_value.split(':', 1)
    else:
        attr_name, attr_value = attr_name_value, True

    current_attrs = field.field.widget.attrs.copy()
    current_attrs[attr_name] = attr_value
    return field.as_widget(attrs=current_attrs)
