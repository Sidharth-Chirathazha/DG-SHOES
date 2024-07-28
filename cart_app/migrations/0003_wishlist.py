# Generated by Django 5.0.6 on 2024-07-27 04:56

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cart_app', '0002_alter_cartitem_quantity'),
        ('product_app', '0008_product_featured'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Wishlist',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('product_variant', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='product_app.productcolorimage')),
                ('size_variant', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='product_app.productsize')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'unique_together': {('user', 'product_variant', 'size_variant')},
            },
        ),
    ]
