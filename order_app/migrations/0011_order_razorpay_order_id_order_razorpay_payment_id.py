# Generated by Django 5.0.6 on 2024-08-04 10:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('order_app', '0010_alter_order_payment_method'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='razorpay_order_id',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='order',
            name='razorpay_payment_id',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]