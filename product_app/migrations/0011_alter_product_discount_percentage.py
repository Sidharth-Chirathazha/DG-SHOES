# Generated by Django 5.0.6 on 2024-08-03 12:53

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product_app', '0010_product_discounted_price'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='discount_percentage',
            field=models.IntegerField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(99)]),
        ),
    ]