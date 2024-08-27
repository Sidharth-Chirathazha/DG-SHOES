from django.db import models
from category_app.models import Category,SubCategory
from django.utils.text import slugify
from PIL import Image
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal
from offer_app.models import Offer

# Create your models here.


class Product(models.Model):

    product_name = models.CharField(max_length=300,null=False,blank=False)
    description = models.CharField(max_length=500,null=True,blank=True)
    price = models.DecimalField(max_digits=10,decimal_places=2,null=False)
    category_id = models.ForeignKey(Category,null=True,on_delete=models.SET_NULL)
    subcategory_id = models.ForeignKey(SubCategory,null=True,on_delete=models.SET_NULL)
    slug = models.SlugField(max_length=500, unique=True, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_listed = models.BooleanField(default=True)
    featured = models.BooleanField(default=False)
    is_offer_applied = models.BooleanField(default=False)
    applied_offer = models.ForeignKey(Offer, null=True, blank=True, on_delete=models.SET_NULL, related_name='products_applied')
    discount_percentage = models.IntegerField(null=True, blank=True, validators=[MinValueValidator(1), MaxValueValidator(99)])
    discounted_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, editable=False) 
    
    def __str__(self):

        return self.product_name 
    

    def get_highest_discount_percentage(self):
        product_discount = self.discount_percentage if self.discount_percentage else 0
        subcategory_discount = 0
        
        # Check if there's an offer applied to the subcategory
        if self.subcategory_id and self.subcategory_id.is_offer_applied:
            # Assuming `SubCategory` has a field `discount_percentage` to store the discount
            subcategory_discount = self.subcategory_id.discount_percentage if self.subcategory_id.discount_percentage else 0
        
        return max(product_discount, subcategory_discount)
    

    def get_discounted_price(self):
        discount_percentage = self.get_highest_discount_percentage()
        if discount_percentage:
            return self.price * (1 - Decimal(discount_percentage) / 100)
        return self.price
    
    def save(self, *args, **kwargs):
        # Override discount_percentage with the highest available discount
        self.discount_percentage = self.get_highest_discount_percentage()
        # Calculate the discounted price based on the overridden discount percentage
        self.discounted_price = self.get_discounted_price()
        super(Product, self).save(*args, **kwargs)

    
    

class ProductColorImage(models.Model):

    color_name = models.CharField(max_length=50,null=False,blank=False)
    product_id = models.ForeignKey(Product,on_delete=models.CASCADE)
    image_1 = models.ImageField(upload_to='product_images/', null=True, blank=True)
    image_2 = models.ImageField(upload_to='product_images/', null=True, blank=True)
    image_3 = models.ImageField(upload_to='product_images/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_listed = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.product_id.product_name} - {self.color_name}"
    
        

class ProductSize(models.Model):
    SIZE_CHOICES = [
        ('6', '6'),
        ('7', '7'),
        ('8', '8'),
        ('9', '9'),
        ('10', '10'),
    ]

    size = models.CharField(max_length=2,choices=SIZE_CHOICES,null=False,blank=False)
    product_data = models.ForeignKey(ProductColorImage,related_name="product_size",on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
         return f"{self.size} of {self.product_data}"