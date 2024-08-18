from django.db import models
from user.models import CustomUser

# Create your models here.

class Wallet(models.Model):

    user = models.OneToOneField(CustomUser,on_delete=models.CASCADE,related_name='wallet')
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s Wallet"
    
    def credit(self,amount):
        self.balance += amount
        self.save()

    def debit(self, amount):
        if amount > self.balance:
            raise ValueError("Insufficient balance in wallet")
        self.balance -= amount
        self.save()



class WalletTransaction(models.Model):
    TRANSACTION_TYPES = (
        ('credit', 'Credit'),
        ('debit', 'Debit'),
    )


    TRANSACTION_DESCRIPTIONS = (
        ('purchase', 'Purchase using wallet'),
        ('return', 'Refund for returned product'),
        ('cancellation', 'Refund for cancelled order via Razor Pay/Wallet'),
        ('referral', 'Bonus amount for referral')
    )

    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE, related_name='transactions')
    transaction_type = models.CharField(max_length=6, choices=TRANSACTION_TYPES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    timestamp = models.DateTimeField(auto_now_add=True)
    description = models.CharField(max_length=255,choices=TRANSACTION_DESCRIPTIONS)

    def __str__(self):
        return f"{self.transaction_type.capitalize()} of {self.amount} to {self.wallet.user.username}'s Wallet"

    def save(self, *args, **kwargs):
        if self.transaction_type == 'credit':
            self.wallet.credit(self.amount)
        elif self.transaction_type == 'debit':
            self.wallet.debit(self.amount)
        super().save(*args, **kwargs)
