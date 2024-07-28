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