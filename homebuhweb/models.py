from django.db import models

# Тестовая модель для создания миграций
class TestModel(models.Model):
    name = models.CharField(max_length=100)
