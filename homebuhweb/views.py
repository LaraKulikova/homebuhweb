import datetime
from decimal import Decimal, ROUND_HALF_UP
import requests
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import Group

from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.shortcuts import render, redirect
from django.templatetags.static import static
from .forms import ExpenseForm
from .forms import UserForm, ProfileForm
from .models import Category, SubCategory, SubSubCategory, Expense
from .models import Income, Profile
from datetime import datetime, date


def homepage(request):
    return render(request, 'homebuhweb/homepage.html')


def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            group = Group.objects.get(name='Users')
            user.groups.add(group)
            login(request, user)
            return redirect('user_cabinet')
    else:
        form = UserCreationForm()
    return render(request, 'homebuhweb/login/register.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('user_cabinet')
    else:
        form = AuthenticationForm()
    return redirect('homepage')


@login_required
def user_cabinet(request):
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    total_income = Decimal('0.00')
    total_income_usd = Decimal('0.00')
    total_income_eur = Decimal('0.00')
    total_income_rub = Decimal('0.00')

    user = request.user
    profile = get_object_or_404(Profile, user=user)

    if request.method == 'POST':
        user_form = UserForm(request.POST, instance=user)
        profile_form = ProfileForm(request.POST, request.FILES, instance=profile)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
    else:
        user_form = UserForm(instance=user)
        profile_form = ProfileForm(instance=profile)

    if start_date and end_date:
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
        incomes = Income.objects.filter(user=request.user, date__range=[start_date, end_date])
        total_income = sum(income.amount for income in incomes)

        # Получение курсов валют
        currency_rates = get_currency_rates()
        usd_rate = currency_rates.get('USD', Decimal('1'))
        eur_rate = currency_rates.get('EUR', Decimal('1'))
        rub_rate = currency_rates.get('RUB', Decimal('1'))

        total_income_usd = (total_income / usd_rate).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        total_income_eur = (total_income / eur_rate).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        total_income_rub = (total_income / (rub_rate / Decimal('100'))).quantize(Decimal('0.01'),
                                                                                 rounding=ROUND_HALF_UP)

    return render(request, 'homebuhweb/login/usercabinet.html', {
        'start_date': start_date,
        'end_date': end_date,
        'total_income': total_income,
        'total_income_usd': total_income_usd,
        'total_income_eur': total_income_eur,
        'total_income_rub': total_income_rub,
        'user_form': user_form,
        'profile_form': profile_form,
        'avatar_url': profile.avatar.url if profile.avatar else static('images/apple-touch-icon.png'),
        'username': user.get_full_name() or user.username,
    })


@login_required
def user_prof(request):
    if request.method == 'POST':
        user_form = UserForm(request.POST, instance=request.user)
        profile_form = ProfileForm(request.POST, request.FILES, instance=request.user.profile)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            return redirect('user_prof')
    else:
        user_form = UserForm(instance=request.user)
        profile_form = ProfileForm(instance=request.user.profile)

    return render(request, 'homebuhweb/login/user_prof.html', {
        'user_form': user_form,
        'profile_form': profile_form
    })


@login_required
def delete_avatar(request):
    user = request.user
    user.profile.avatar.delete()
    return redirect('user_prof')


@login_required
def add_income(request, id=None):
    if id:
        income = get_object_or_404(Income, id=id, user=request.user)
    else:
        income = None

    if request.method == 'POST':
        income_type = request.POST['income_type']
        amount = request.POST['amount']
        date = request.POST['date']

        if income:
            income.income_type = income_type
            income.amount = amount
            income.date = date
            income.save()
        else:
            Income.objects.create(user=request.user, income_type=income_type, amount=amount, date=date)

        return redirect('add_income')

    incomes = Income.objects.filter(user=request.user)
    return render(request, 'homebuhweb/incomes/add_income.html', {'income': income, 'incomes': incomes})


@login_required
def delete_income(request, id):
    income = get_object_or_404(Income, id=id)
    income.delete()
    return redirect('add_income')


def get_currency_rates():
    url = 'https://www.nbrb.by/api/exrates/rates?periodicity=0'
    response = requests.get(url)
    data = response.json()

    rates = {}
    currencies = ['USD', 'EUR', 'RUB']
    for rate in data:
        if rate['Cur_Abbreviation'] in currencies:
            rates[rate['Cur_Abbreviation']] = Decimal(str(rate['Cur_OfficialRate']))

    return rates


@login_required
def add_expense(request):
    if request.method == 'POST':
        form = ExpenseForm(request.POST)

        if form.is_valid():
            expense = form.save(commit=False)
            expense.user = request.user
            expense.save()
            form = ExpenseForm()  # Очистить форму после сохранения
        else:
            print("Form is not valid:", form.errors)  # Отладочное сообщение
    else:
        form = ExpenseForm()

    categories = Category.objects.all()
    expenses_today = Expense.objects.filter(user=request.user, date=date.today())

    context = {
        'form': form,
        'categories': categories,
        'expenses_today': expenses_today,
        'current_date': date.today()
    }

    return render(request, 'homebuhweb/expenses/add_expenses.html', context)


@login_required
def edit_expense(request, expense_id):
    expense = get_object_or_404(Expense, id=expense_id, user=request.user)

    if request.method == 'POST':
        form = ExpenseForm(request.POST, instance=expense)

        if form.is_valid():
            form.save()
            return redirect('add_expense')
    else:
        form = ExpenseForm(instance=expense)

    return render(request, 'homebuhweb/expenses/edit_expense.html', {'form': form, 'expense': expense})


@login_required
def delete_expense(request, expense_id):
    expense = get_object_or_404(Expense, id=expense_id, user=request.user)
    expense.delete()
    return redirect('add_expense')


@login_required
def get_subcategories(request, category_id):
    subcategories = SubCategory.objects.filter(category_id=category_id)
    return JsonResponse(list(subcategories.values('id', 'name')), safe=False)


def get_subsubcategories(request, subcategory_id):
    subsubcategories = SubSubCategory.objects.filter(subcategory_id=subcategory_id)
    return JsonResponse(list(subsubcategories.values('id', 'name')), safe=False)
