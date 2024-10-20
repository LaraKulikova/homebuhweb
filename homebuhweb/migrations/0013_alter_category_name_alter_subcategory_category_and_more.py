# Generated by Django 5.1.1 on 2024-10-18 06:49

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('homebuhweb', '0012_merge_20241018_0610'),
    ]

    operations = [
        migrations.AlterField(
            model_name='category',
            name='name',
            field=models.CharField(max_length=100),
        ),
        migrations.AlterField(
            model_name='subcategory',
            name='category',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='homebuhweb.category'),
        ),
        migrations.AlterField(
            model_name='subsubcategory',
            name='subcategory',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='homebuhweb.subcategory'),
        ),
    ]
