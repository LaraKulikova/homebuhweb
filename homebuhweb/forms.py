from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm


class UserRegisterForm(UserCreationForm):
    email = forms.EmailField(label='Электронная почта')

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
        labels = {
            'username': 'Имя пользователя',
            'password1': 'Пароль',
            'password2': 'Подтверждение пароля',
        }
        help_texts = {
            'username': 'Обязательно. Не более 150 символов. Только буквы, цифры и @/./+/-/_',
            'password1': 'Ваш пароль должен содержать не менее 8 символов, не должен быть слишком распространенным и не должен состоять только из цифр.',
            'password2': 'Введите тот же пароль, что и выше, для проверки.',
        }
        error_messages = {
            'username': {
                'max_length': 'Имя пользователя не может быть длиннее 150 символов.',
                'required': 'Это поле обязательно.',
            },
            'password1': {
                'required': 'Это поле обязательно.',
            },
            'password2': {
                'required': 'Это поле обязательно.',
                'password_mismatch': 'Пароли не совпадают.',
            },
        }
