# Generated by Django 5.0.6 on 2024-07-04 15:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product_app', '0002_productsize'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='product_name',
            field=models.CharField(max_length=100),
        ),
        migrations.AlterField(
            model_name='productsize',
            name='size',
            field=models.CharField(choices=[('6', '6'), ('7', '7'), ('8', '8'), ('9', '9'), ('10', '10')], max_length=2),
        ),
    ]
