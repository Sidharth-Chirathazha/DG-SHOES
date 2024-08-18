# your_app/templatetags/custom_filters.py
from django import template

register = template.Library()

@register.filter(name='not_in_list')
def not_in_list(value, status_list):
    return value not in status_list.split(',')



@register.filter
def is_paid_or_pending_cod(order):
    return order.payment_status == 'Paid' or (
        order.payment_status == 'Pending' and order.payment_method == 'COD'
    )