from django.db import migrations


def add_categories(apps, schema_editor):
    Category = apps.get_model('homebuhweb', 'Category')
    categories = [
        'жилье',
        'продукты питания',
        'транспорт',
        'спорт',
        'здоровье',
        'образование',
        'прочие расходы'
    ]
    for category_name in categories:
        Category.objects.create(name=category_name)


class Migration(migrations.Migration):
    dependencies = [
        ('homebuhweb', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(add_categories),
    ]
