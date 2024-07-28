# your_app/templatetags/custom_filters.py
from django import template

register = template.Library()

@register.filter(name='not_in_list')
def not_in_list(value, status_list):
    return value not in status_list.split(',')