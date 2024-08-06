from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
import uuid
from django.utils import timezone
from django.core.exceptions import ValidationError
import random
import string


class Coupons(models.Model):
    title = models.CharField(max_length=30, blank=True)
    description = models.CharField(max_length=200,blank=True)
    code = models.CharField(max_length=20, unique=True, default="xxxx")
    valid_from = models.DateTimeField(null=True, blank=True)
    expiry = models.DateTimeField(null=True, blank=True)
    discount_amount = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )
    discount_percentage = models.PositiveIntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(100)], blank=True, null=True
    )
    min_limit = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    is_active = models.BooleanField(default=False)
    created_on = models.DateTimeField(auto_now_add=True)
    

    def __str__(self):
        return self.title

    def clean(self):
        super().clean()
        if not self.discount_amount and not self.discount_percentage:
            raise ValidationError('Either discount_amount or discount_percentage must be set.')
        if self.discount_amount and self.discount_percentage:
            raise ValidationError('Only one of discount_amount or discount_percentage can be set.')

    def save(self, *args, **kwargs):
        if self.code == "xxxx":
            self.code = self.generate_unique_code()
        super().save(*args, **kwargs)
    
    def generate_unique_code(self):
        while True:

            code = random.choice(string.ascii_uppercase) + ''.join(random.choices(string.ascii_uppercase + string.digits,k=6))

            if not Coupons.objects.filter(code=code).exists():
                return code
            
    def is_expired(self):
        if self.expiry:
            return timezone.now() > self.expiry
        return False
    
    def update_active_status(self):
        if self.is_expired() and self.is_active:
            self.is_active = False
            self.save()
            

