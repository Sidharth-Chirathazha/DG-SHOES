from django.contrib import admin
from .models import WalletTransaction,Wallet

# Register your models here.
admin.site.register(Wallet)
admin.site.register(WalletTransaction)