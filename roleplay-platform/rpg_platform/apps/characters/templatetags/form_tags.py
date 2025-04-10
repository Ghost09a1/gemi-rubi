from django import template

register = template.Library()

@register.filter(name='add_class')
def add_class(field, css_class):
    """Add a CSS class to a form field."""
    return field.as_widget(attrs={'class': css_class})

@register.filter(name='attr')
def set_attr(field, attr_name_value):
    """Set an attribute on a form field.

    Usage: {{ field|attr:'required' }} or {{ field|attr:'data-toggle:modal' }}
    """
    if ':' in attr_name_value:
        attr_name, attr_value = attr_name_value.split(':', 1)
    else:
        attr_name, attr_value = attr_name_value, True

    current_attrs = field.field.widget.attrs
    current_attrs[attr_name] = attr_value
    return field.as_widget(attrs=current_attrs)
