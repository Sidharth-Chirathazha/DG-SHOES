# Generated by Django 5.0.6 on 2024-08-12 09:29

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('category_app', '0012_alter_subcategory_discount_percentage'),
        ('offer_app', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='subcategory',
            name='applied_offer',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='subcategories_applied', to='offer_app.offer'),
        ),
    ]