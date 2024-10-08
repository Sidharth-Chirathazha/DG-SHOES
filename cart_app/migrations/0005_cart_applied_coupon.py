# Generated by Django 5.0.6 on 2024-08-03 18:37

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cart_app', '0004_alter_wishlist_unique_together_and_more'),
        ('coupon_app', '0002_remove_coupons_max_limit_coupons_description'),
    ]

    operations = [
        migrations.AddField(
            model_name='cart',
            name='applied_coupon',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='coupon_app.coupons'),
        ),
    ]
