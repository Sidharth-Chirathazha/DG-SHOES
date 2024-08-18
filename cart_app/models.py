from django.db import models
from django.core.exceptions import ValidationError
from user.models import CustomUser
from product_app.models import Product,ProductColorImage,ProductSize
from coupon_app.models import Coupons

# Create your models here.

class Cart(models.Model):

    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='users')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    applied_coupon = models.ForeignKey(Coupons,blank=True,null=True,on_delete=models.SET_NULL)

    def __str__(self):
        return f"Cart of {self.user.username}"
    
    def get_total_items(self):

        return self.items.count()
    

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE,related_name='products')
    product_size = models.ForeignKey(ProductSize, on_delete=models.CASCADE, related_name='size_variants')
    product_color = models.ForeignKey(ProductColorImage, on_delete=models.CASCADE,related_name='color_variants')
    quantity = models.PositiveIntegerField(default=0)
    
    def __str__(self):
        return f"{self.quantity} of {self.product_size} ({self.product_color.color_name})"
    
    def get_total_price(self):
        if self.product.is_offer_applied:
            return self.product.discounted_price * self.quantity
        else:
            return self.product.price * self.quantity
    
    def clean(self):
        if self.quantity > self.product_size.quantity:
            raise ValidationError('Quantity exceeds avilable stock')
        
    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)


class Wishlist(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    product_variant = models.ForeignKey(ProductColorImage, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'product_variant')

    def __str__(self):
        return f"{self.user.username} - {self.product_variant.product_id.product_name} ({self.product_variant.color_name}"