from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, User
from django.contrib.auth.models import User
from django.contrib.auth.models import User
from django.db import models


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


# class UserRegisterForm(UserCreationForm):
#     email = forms.EmailField(label='Электронная почта')
#
#     class Meta:
#         model = User
#         fields = ['username', 'email', 'password1', 'password2']
#         labels = {
#             'username': 'Имя пользователя',
#             'password1': 'Пароль',
#             'password2': 'Подтверждение пароля',
#         }
#         help_texts = {
#             'username': 'Обязательно. Не более 150 символов. Только буквы, цифры и @/./+/-/_',
#             'password1': 'Ваш пароль должен содержать не менее 8 символов, не должен быть слишком распространенным и не должен состоять только из цифр.',
#             'password2': 'Введите тот же пароль, что и выше, для проверки.',
#         }
#         error_messages = {
#             'username': {
#                 'max_length': 'Имя пользователя не может быть длиннее 150 символов.',
#                 'required': 'Это поле обязательно.',
#             },
#             'password1': {
#                 'required': 'Это поле обязательно.',
#             },
#             'password2': {
#                 'required': 'Это поле обязательно.',
#                 'password_mismatch': 'Пароли не совпадают.',
#             },
#         }
