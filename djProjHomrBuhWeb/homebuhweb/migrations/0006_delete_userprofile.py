# Generated by Django 5.1.1 on 2024-10-14 01:26

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('homebuhweb', '0005_remove_profile_can_create_data_profile_address_and_more'),
    ]

    operations = [
        migrations.DeleteModel(
            name='UserProfile',
        ),
    ]
