# Generated by Django 5.1.1 on 2024-10-19 12:25

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('homebuhweb', '0013_alter_category_name_alter_subcategory_category_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='CarExpense',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('car_brand', models.CharField(max_length=100)),
                ('mileage', models.PositiveIntegerField()),
                ('amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('description', models.CharField(max_length=250)),
                ('date', models.DateField()),
                ('subsubcategory', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='car_expenses', to='homebuhweb.expense')),
            ],
        ),
    ]
