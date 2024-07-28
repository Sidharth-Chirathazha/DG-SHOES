from django.db import models
from django.utils.text import slugify
from PIL import Image

# Create your models here.

class Category(models.Model):

    category_name = models.CharField(max_length=100,unique=True,null=False,blank=False)
    image = models.ImageField(upload_to='category_images/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True,auto_now=False)
    updated_at = models.DateTimeField(auto_now=True,auto_now_add=False)
    is_listed = models.BooleanField(default=True)
    
    def __str__(self):

        return self.category_name
    
    
class SubCategory(models.Model):

    subcategory_name = models.CharField(max_length=100,null=False,blank=False)
    category = models.ForeignKey(Category,related_name="subcategories",on_delete=models.CASCADE)
    image = models.ImageField(upload_to='subcategory_images/', null=True, blank=True)
    slug = models.SlugField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True,auto_now=False)
    updated_at = models.DateTimeField(auto_now=True,auto_now_add=False)
    is_listed = models.BooleanField(default=True)

    class Meta:
        unique_together = ('subcategory_name', 'category')  # Ensure subcategory names are unique within a category

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(f'{self.category.category_name}-{self.subcategory_name}')
        super(SubCategory, self).save(*args, **kwargs)
       
    def __str__(self):

        return self.subcategory_name