# Generated by Django 5.1.1 on 2024-10-18 03:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('homebuhweb', '0010_category_user'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='category',
            name='user',
        ),
        migrations.AlterField(
            model_name='category',
            name='name',
            field=models.CharField(max_length=100, unique=True),
        ),
    ]
