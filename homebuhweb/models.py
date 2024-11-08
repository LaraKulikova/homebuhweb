from decimal import Decimal

from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, User
from django.contrib.auth.models import User
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from django.db import models
from django.contrib.auth.models import User


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    phone = models.CharField(max_length=15, blank=True)
    address = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return self.user.username


class Income(models.Model):
    INCOME_TYPES = [
        ('заработная плата', 'Заработная плата'),
        ('пенсия', 'Пенсия'),
        ('стипендия', 'Стипендия'),
        ('выигрыш', 'Выигрыш'),
        ('доходы от индивидуальной предпринимательской деятельности',
         'Доходы от индивидуальной предпринимательской деятельности'),
        ('доходы от недвижимости', 'Доходы от недвижимости'),
        ('доходы от депозита', 'Доходы от депозита'),
        ('подарки', 'Подарки'),
        ('наличные денежные средства', 'Наличные денежные средства'),
        ('прочие доходы', 'Прочие доходы'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    income_type = models.CharField(max_length=100, choices=INCOME_TYPES)
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))])
    date = models.DateField()

    def __str__(self):
        return f"{self.income_type} - {self.amount}"


class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class SubCategory(models.Model):
    name = models.CharField(max_length=100)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class SubSubCategory(models.Model):
    name = models.CharField(max_length=100)
    subcategory = models.ForeignKey(SubCategory, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class Expense(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    subcategory = models.ForeignKey(SubCategory, on_delete=models.CASCADE)
    subsubcategory = models.ForeignKey(SubSubCategory, on_delete=models.CASCADE, null=True, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField()

    def __str__(self):
        return f"{self.category} - {self.subcategory} - {self.subsubcategory} - {self.amount}"


class CarExpense(models.Model):
    car_brand = models.CharField(max_length=100)
    mileage = models.PositiveIntegerField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.CharField(max_length=250)
    date = models.DateField()
    subsubcategory = models.ForeignKey(Expense, on_delete=models.CASCADE, related_name='car_expenses')

    def __str__(self):
        return f"{self.car_brand} - {self.amount}"


class PlannedExpense(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    item_name = models.CharField(max_length=255)
    start_date = models.DateField()

    item_cost = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )

    months_to_save = models.IntegerField(
        validators=[MinValueValidator(1)]
    )

    monthly_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True
    )

    def calculate_monthly_amount(self):
        if self.months_to_save > 0:
            return self.item_cost / self.months_to_save
        return Decimal('0.00')

    def save(self, *args, **kwargs):
        self.monthly_amount = self.calculate_monthly_amount()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.item_name} - {self.item_cost}"


class Credit(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    credit_name = models.CharField(max_length=255)
    credit_amount = models.PositiveIntegerField()
    credit_term = models.IntegerField()
    interest_rate = models.DecimalField(max_digits=5, decimal_places=2)
    issue_date = models.DateField()
    is_paid_off = models.BooleanField(default=False)  # Новое поле

    def __str__(self):
        return self.credit_name

    @property
    def principal_amount(self):
        return Decimal(self.credit_amount) / Decimal(self.credit_term)

    @property
    def monthly_interest(self):
        return (Decimal(self.credit_amount) * (self.interest_rate / Decimal(100))) / Decimal(12)

    @property
    def monthly_payment(self):
        return self.principal_amount + self.monthly_interest
