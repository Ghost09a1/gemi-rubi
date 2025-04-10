from django import template
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _

register = template.Library()


@register.simple_tag(takes_context=True)
def url_replace(context, **kwargs):
    """
    Template tag to replace URL parameters while keeping existing ones.
    Useful for pagination with query parameters.

    Usage:
    <a href="?{% url_replace page=1 %}">First page</a>
    """
    query_dict = context['request'].GET.copy()
    for key, value in kwargs.items():
        query_dict[key] = value
    return query_dict.urlencode()


@register.filter
def status_badge(status):
    """
    Return a Bootstrap badge with the appropriate color for a report status.

    Usage:
    {{ report.status|status_badge }}
    """
    colors = {
        'pending': 'warning',
        'investigating': 'info',
        'resolved': 'success',
        'rejected': 'secondary'
    }
    labels = {
        'pending': _('Pending Review'),
        'investigating': _('Under Investigation'),
        'resolved': _('Resolved'),
        'rejected': _('Rejected')
    }

    color = colors.get(status, 'primary')
    label = labels.get(status, status)

    return mark_safe(f'<span class="badge bg-{color}">{label}</span>')


@register.filter
def report_type_badge(report_type):
    """
    Return a Bootstrap badge with the appropriate color for a report type.

    Usage:
    {{ report.report_type|report_type_badge }}
    """
    colors = {
        'spam': 'secondary',
        'inappropriate': 'danger',
        'harassment': 'warning',
        'other': 'info'
    }

    color = colors.get(report_type, 'primary')

    return mark_safe(f'<span class="badge bg-{color}">{report_type}</span>')


@register.filter
def timeago(date):
    """
    Format a date as a human-readable "time ago" string.

    Usage:
    {{ report.created_at|timeago }}
    """
    from django.utils import timezone
    from django.utils.timesince import timesince

    now = timezone.now()
    diff = now - date

    if diff.days == 0 and diff.seconds < 60:
        return _('Just now')

    return _('%(time)s ago') % {'time': timesince(date).split(',')[0]}


@register.filter
def pprint(value):
    """
    Pretty print a JSON dictionary or any Python object.

    Usage:
    {{ log.additional_data|pprint }}
    """
    import json
    import pprint as pp

    if isinstance(value, dict):
        try:
            return json.dumps(value, indent=2, sort_keys=True)
        except (TypeError, ValueError):
            return pp.pformat(value)
    return pp.pformat(value)


@register.filter
def divide(value, arg):
    """
    Divide the value by the argument

    Usage:
    {{ value|divide:arg }}
    """
    try:
        return float(value) / float(arg)
    except (ValueError, ZeroDivisionError):
        return 0

@register.filter
def multiply(value, arg):
    """
    Multiply the value by the argument

    Usage:
    {{ value|multiply:arg }}
    """
    try:
        return float(value) * float(arg)
    except ValueError:
        return 0

@register.filter
def get_range(value):
    """
    Return a range of numbers from 1 to value (inclusive)
    Useful for pagination in templates.

    Usage:
    {% for i in total_pages|get_range %}
        {{ i }}
    {% endfor %}
    """
    return range(1, int(value) + 1)

@register.filter
def get_item(dictionary, key):
    """
    Get an item from a dictionary using a variable as the key.
    Useful for accessing dict items in templates.

    Usage:
    {{ my_dict|get_item:my_key }}
    """
    return dictionary.get(key, '')
