from django.db import models
from django.contrib.auth.models import AbstractUser
from phonenumber_field.modelfields import PhoneNumberField
from django.utils.crypto import get_random_string


# Create your models here.

class CustomUser(AbstractUser):

    phone_number = PhoneNumberField(unique = True, blank = True, null = True)
    date_of_birth = models.DateField(null=True, blank=True)
    referral_code = models.CharField(max_length=6, unique=True, blank=True, null=True)
    referred_by = models.ForeignKey('self', on_delete=models.SET_NULL, blank=True, null=True, related_name='referrals')

    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
    ]
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, null=True, blank=True)


    def save(self, *args, **kwargs):
        if not self.referral_code:
            self.referral_code = self.generate_unique_referral_code()
        super().save(*args, **kwargs)

    def generate_unique_referral_code(self):
        while True:
            code = f"DG{get_random_string(4, allowed_chars='0123456789')}"
            if not CustomUser.objects.filter(referral_code=code).exists():
                return code

    

    def __str__(self):
        
        return self.username
    
# class OtpToken(models.Model):

#     user = models.OneToOneField(CustomUser, on_delete=models.CASCADE,related_name="otps")
#     otp_code = models.CharField(max_length=6,default=secrets.token_hex(3))
#     otp_created_at = models.DateTimeField(auto_now_add=True)
#     otp_expires_at = models.DateTimeField(blank=True,null=True)

#     def __str__(self):

#         return self.user.username

