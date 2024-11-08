from django import forms
from django.contrib.auth.models import User

from .models import CarExpense
from .models import Expense
from .models import Profile, PlannedExpense, Credit


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['avatar', 'phone', 'address']
        labels = {
            'avatar': 'Аватар',
            'phone': 'Телефон',
            'address': 'Адрес',
        }


class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
        labels = {
            'first_name': 'Имя',
            'last_name': 'Фамилия',
            'email': 'Электронная почта',
        }





from django import forms
from .models import Expense

class ExpenseForm(forms.ModelForm):
    class Meta:
        model = Expense
        fields = ['category', 'subcategory', 'subsubcategory', 'amount', 'date']

    def clean_amount(self):
        amount = self.cleaned_data.get('amount')
        if amount < 0:
            raise forms.ValidationError('Сумма не может быть отрицательной')
        return amount





class CarExpenseForm(forms.ModelForm):
    class Meta:
        model = CarExpense
        fields = ['car_brand', 'mileage', 'amount', 'description', 'date']
        labels = {
            'car_brand': 'Марка автомобиля',
            'mileage': 'Пробег',
            'amount': 'Сумма',
            'description': 'Описание товара',
            'date': 'Дата',
        }
        widgets = {
            'car_brand': forms.TextInput(attrs={'class': 'form-control', 'style': 'background-color: #ffffff;'}),
            'mileage': forms.NumberInput(attrs={'class': 'form-control', 'style': 'background-color: #ffffff;'}),
            'amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'readonly': 'readonly',
                'style': 'background-color: #A78B71; color: #ffffff;'
            }),
            'description': forms.TextInput(attrs={'class': 'form-control', 'style': 'background-color: #ffffff;'}),
            'date': forms.TextInput(attrs={
                'class': 'form-control',
                'readonly': 'readonly',
                'style': 'background-color: #A78B71; color: #ffffff;'
            }),
        }


class PlannedExpenseForm(forms.ModelForm):
    class Meta:
        model = PlannedExpense
        fields = ['item_name', 'start_date', 'item_cost', 'months_to_save']

        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
        }

        labels = {
            'item_name': 'Наименование планируемой покупки',
            'start_date': 'Дата начала накопления',
            'item_cost': 'Стоимость покупки',
            'months_to_save': 'Количество месяцев за которые нужно накопить',
        }


class CreditForm(forms.ModelForm):
    class Meta:
        model = Credit
        fields = ['credit_name', 'credit_amount', 'credit_term', 'interest_rate', 'issue_date']
        widgets = {
            'issue_date': forms.DateInput(attrs={'type': 'date'}),
        }
        labels = {
            'credit_name': 'Название кредита',
            'credit_amount': 'Сумма кредита',
            'credit_term': 'Срок кредита',
            'interest_rate': 'Процентная ставка',
            'issue_date': 'Дата выдачи',
        }
