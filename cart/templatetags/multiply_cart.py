from django import template

register = template.Library()

@register.filter
def multiply(value, arg):
    """Умножает value на arg."""
    return value * arg
