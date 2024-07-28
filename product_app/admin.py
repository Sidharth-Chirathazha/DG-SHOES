from django.contrib import admin
from .models import Product,ProductColorImage,ProductSize

# Register your models here.
admin.site.register(Product)
admin.site.register(ProductColorImage)
admin.site.register(ProductSize)
