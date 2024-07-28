# Generated by Django 5.0.6 on 2024-07-16 11:28

import django.db.models.deletion
import phonenumber_field.modelfields
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Address',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(default='add', max_length=50)),
                ('address_type', models.CharField(default='Home', max_length=50)),
                ('state', models.CharField(max_length=100)),
                ('city', models.CharField(max_length=100)),
                ('pin', models.CharField(max_length=6)),
                ('post_office', models.CharField(max_length=100)),
                ('phone_number', phonenumber_field.modelfields.PhoneNumberField(max_length=128, region=None, unique=True)),
                ('address_line', models.TextField()),
                ('landmark', models.CharField(blank=True, max_length=255, null=True)),
                ('is_listed', models.BooleanField(default=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='addresses', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
