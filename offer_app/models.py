from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator



# Create your models here.

class Offer(models.Model):

    OFFER_TYPES = (
        ('product', 'Product'),
        ('subcategory', 'Subcategory'),
    )

    name = models.CharField(max_length=100)
    discount_percentage = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    offer_type = models.CharField(max_length=20, choices=OFFER_TYPES, default='product')

    def __str__(self):
        return self.name

    def is_valid(self):
        now = timezone.now()
        return self.is_active and self.start_date <= now <= self.end_date
       
    def update_active_status(self):
        from product_app.models import Product
        from category_app.models import SubCategory
        if not self.is_valid() :
            self.is_active = False
            if self.offer_type == 'subcategory':
                applied_subcategories = SubCategory.objects.filter(applied_offer=self)
                for subcategory in applied_subcategories:
                    subcategory.is_offer_applied = False
                    subcategory.discount_percentage = 0
                    subcategory.applied_offer = None
            applied_products = Product.objects.filter(applied_offer = self)
            for product in applied_products:
                product.is_offer_applied = False
                product.discount_percentage = 0
                product.applied_offer = None
                product.save()
            self.save()