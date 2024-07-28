from django.db import models
from user.models import CustomUser
from phonenumber_field.modelfields import PhoneNumberField
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator

# Create your models here.

def validate_pin(value):
    """Ensure pin code is exactly 6 digits."""
    if not value.isdigit() or len(value) != 6:
        raise ValidationError('PIN must be exactly 6 digits.')

class Address(models.Model):

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='addresses')
    name = models.CharField(max_length=50,blank=False)
    address_title = models.CharField(max_length=50, default="Home", blank=False, null=False)
    state = models.CharField(max_length=100,blank = False,null=False)
    city = models.CharField(max_length=100,blank = False,null=False)
    pin = models.CharField(max_length=6,blank = False,null=False,validators=[validate_pin])
    post_office = models.CharField(max_length=100, blank=False, null=False)
    phone_number = PhoneNumberField(unique = False)
    address_line = models.TextField(blank=False,null=False)
    landmark = models.CharField(max_length=255, blank=True, null=True)
    is_listed = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name}, {self.address_title}, {self.city}, {self.state}"
