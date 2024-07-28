from django.db.models.signals import post_delete,post_save,pre_save
from django.dispatch import receiver
from .models import CartItem


# @receiver(post_save, sender=CartItem)
# def update_stock_on_save(sender,instance,created,**kwargs):

#     if created:

#         # new item added to the cart
#         instance.product_size.quantity -= instance.quantity 
#         instance.product_size.save()

#     else:

#         # existing cart item updated
#         previous = CartItem.objects.get(id=instance.id)
#         qauntity_change = instance.quantity - previous.quantity
#         instance.product_size.quantity -= qauntity_change
#         instance.product_size.save()

# @receiver(pre_save, sender=CartItem)
# def update_stock_on_pre_save(sender, instance, **kwargs):

#     if instance.pk:

#         previous = CartItem.objects.get(pk=instance.pk)
#         instance.product_size.quantity += previous.quantity
#         instance.product_size.save()


# @receiver(post_delete, sender=CartItem)
# def update_stock_on_delete(sender, instance, **kwargs):

#     instance.product_size.quantity += instance.quantity
#     instance.product_size.save()


