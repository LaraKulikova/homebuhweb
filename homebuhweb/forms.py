from django import forms
from django.contrib.auth.models import User

from .models import CarExpense
from .models import Expense
from .models import Profile



class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
        labels = {
            'first_name': 'Имя',
            'last_name': 'Фамилия',
            'email': 'Электронная почта',
        }


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['avatar', 'phone', 'address']
        labels = {
            'avatar': 'Аватар',
            'phone': 'Телефон',
            'address': 'Адрес',
        }


class ExpenseForm(forms.ModelForm):
    subsubcategory_id = forms.CharField(
        label='ID Подподкатегории',
        required=False,
        widget=forms.TextInput(attrs={'readonly': 'readonly'})
    )

    class Meta:
        model = Expense
        fields = ['category', 'subcategory', 'subsubcategory', 'subsubcategory_id', 'amount', 'date']

    def __init__(self, *args, **kwargs):
        super(ExpenseForm, self).__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.fields['subsubcategory_id'].initial = self.instance.subsubcategory.id


class CarExpenseForm(forms.ModelForm):
    class Meta:
        model = CarExpense
        fields = ['car_brand', 'mileage', 'description']


