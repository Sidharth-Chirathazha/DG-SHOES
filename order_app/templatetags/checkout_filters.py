from django import template
from decimal import Decimal

register = template.Library()

@register.filter(name='sub')
def sub(value, arg):
    try:
        return Decimal(value) - Decimal(arg)
    except (ValueError, TypeError):
        return value