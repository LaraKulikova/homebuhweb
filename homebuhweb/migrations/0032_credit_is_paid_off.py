# Generated by Django 5.1.1 on 2024-11-08 10:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('homebuhweb', '0031_remove_credit_is_paid_off'),
    ]

    operations = [
        migrations.AddField(
            model_name='credit',
            name='is_paid_off',
            field=models.BooleanField(default=False),
        ),
    ]