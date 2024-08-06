from django import template

register = template.Library()

@register.filter(name='status_badge_class')
def status_badge_class(status):
    badge_classes = {
        'Pending': 'bg-label-warning',
        'Processing': 'bg-label-info',
        'Shipped': 'bg-label-primary',
        'Delivered': 'bg-label-success',
        'Cancelled': 'bg-label-danger',
    }
    return badge_classes.get(status, 'bg-label-secondary')



@register.filter
def total_order_amount(orders):
    return sum(order.order_amount for order in orders)

@register.filter
def total_discount_amount(orders):
    return sum(order.discount for order in orders)

@register.filter
def total_coupons_deduction(orders):
    return sum(order.coupon_deduction for order in orders)