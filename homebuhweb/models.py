from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, User
from django.contrib.auth.models import User
from django.contrib.auth.models import User
from django.db import models
from django.contrib.auth.models import User


class MyUserManager(BaseUserManager):
    def create_user(self, email, username, password=None):
        if not email:
            raise ValueError('Обязательное поле. Введите адрес электронной почты')
        if not username:
            raise ValueError('Обязательное поле. Введите имя пользователя')

        user = self.model(
            email=self.normalize_email(email),
            username=username,
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, password=None):
        user = self.create_user(
            email,
            username=username,
            password=password,
        )
        user.is_admin = True
        user.save(using=self._db)
        return user


class MyUser(AbstractBaseUser):
    email = models.EmailField(verbose_name='email address', max_length=255, unique=True)
    username = models.CharField(max_length=30, unique=True)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)

    objects = MyUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True

    @property
    def is_staff(self):
        return self.is_admin


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
    amount = models.DecimalField(max_digits=10, decimal_places=2)
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
    item_cost = models.DecimalField(max_digits=10, decimal_places=2)
    months_to_save = models.IntegerField()
    monthly_amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    def calculate_monthly_amount(self):
        if self.months_to_save > 0:
            self.monthly_amount = self.item_cost / self.months_to_save
        else:
            self.monthly_amount = 0
        self.save()

    def __str__(self):
        return self.item_name