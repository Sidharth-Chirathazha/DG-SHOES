from django.db import models
from category_app.models import Category,SubCategory
from django.utils.text import slugify
from PIL import Image

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
    
    

    def __str__(self):

        return self.product_name
    

class ProductColorImage(models.Model):

    color_name = models.CharField(max_length=50,null=False,blank=False)
    product_id = models.ForeignKey(Product,on_delete=models.CASCADE)
    image_1 = models.ImageField(upload_to='product_images/', null=True, blank=True)
    image_2 = models.ImageField(upload_to='product_images/', null=True, blank=True)
    image_3 = models.ImageField(upload_to='product_images/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
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