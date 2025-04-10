from django import template
from django.template.defaultfilters import floatformat
from django.utils.safestring import mark_safe

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """Get an item from a dictionary by key"""
    return dictionary.get(key, '')

@register.filter
def display_score(value, max_value=5):
    """Display a rating score with stars"""
    if not value:
        return mark_safe('<span class="text-muted">No score</span>')

    # Format the numeric score
    formatted_score = floatformat(value, 1)

    # Calculate full and empty stars
    full_stars = int(value)
    half_star = value - full_stars >= 0.5
    empty_stars = max_value - full_stars - (1 if half_star else 0)

    # Build HTML for stars
    html = []

    # Add full stars
    for i in range(full_stars):
        html.append('<i class="fas fa-star text-warning"></i>')

    # Add half star if needed
    if half_star:
        html.append('<i class="fas fa-star-half-alt text-warning"></i>')

    # Add empty stars
    for i in range(empty_stars):
        html.append('<i class="far fa-star text-warning"></i>')

    return mark_safe(f'<span class="rating-stars">{"".join(html)}</span> <span class="rating-value">{formatted_score}</span>')

@register.filter
def div(value, divisor):
    """Divide a value by divisor"""
    try:
        return float(value) / float(divisor)
    except (ValueError, ZeroDivisionError):
        return 0

@register.filter
def mul(value, factor):
    """Multiply a value by factor"""
    try:
        return float(value) * float(factor)
    except ValueError:
        return 0
