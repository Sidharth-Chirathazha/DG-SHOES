from django.db import models
from django.contrib.auth.models import AbstractUser
from phonenumber_field.modelfields import PhoneNumberField


# Create your models here.

class CustomUser(AbstractUser):

    phone_number = PhoneNumberField(unique = True, blank = True, null = True)
    date_of_birth = models.DateField(null=True, blank=True)
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
    ]
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, null=True, blank=True)

    

    def __str__(self):
        
        return self.username
    
# class OtpToken(models.Model):

#     user = models.OneToOneField(CustomUser, on_delete=models.CASCADE,related_name="otps")
#     otp_code = models.CharField(max_length=6,default=secrets.token_hex(3))
#     otp_created_at = models.DateTimeField(auto_now_add=True)
#     otp_expires_at = models.DateTimeField(blank=True,null=True)

#     def __str__(self):

#         return self.user.username

