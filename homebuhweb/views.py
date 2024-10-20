import datetime
from decimal import Decimal, ROUND_HALF_UP
import requests
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import Group
from django.db.models import Sum

from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.shortcuts import render, redirect
from django.templatetags.static import static
from .forms import ExpenseForm, CarExpenseForm
from .forms import UserForm, ProfileForm
from .models import Category, SubCategory, SubSubCategory, Expense
from .models import Income, Profile
from datetime import datetime, date
from .models import PlannedExpense
from .forms import PlannedExpenseForm
from .models import Credit
from .forms import CreditForm



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


def calculate_balance(user):
    incomes = Income.objects.filter(user=user)
    expenses = Expense.objects.filter(user=user)

    total_income = incomes.aggregate(Sum('amount'))['amount__sum'] or 0
    total_expenses = expenses.aggregate(Sum('amount'))['amount__sum'] or 0
    balance = total_income - total_expenses

    return total_income, total_expenses, balance


def user_cabinet(request):
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    total_income = Decimal('0.00')
    total_income_usd = Decimal('0.00')
    total_income_eur = Decimal('0.00')
    total_income_rub = Decimal('0.00')

    total_income, total_expenses, balance = calculate_balance(request.user)

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
        currency_rates = get_currency_rates(request)
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
        'total_expenses': total_expenses,
        'balance': balance,
        'balance_value': balance,
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
    total_income = incomes.aggregate(Sum('amount'))['amount__sum'] or 0

    return render(request, 'homebuhweb/incomes/add_income.html', {
        'income': income,
        'incomes': incomes,
        'total_income': total_income
    })


@login_required
def delete_income(request, id):
    income = get_object_or_404(Income, id=id)
    income.delete()
    return redirect('add_income')


def get_currency_rates(request):
    url = 'https://www.nbrb.by/api/exrates/rates?periodicity=0'
    response = requests.get(url)
    data = response.json()

    rates = {}
    currencies = ['USD', 'EUR', 'RUB']
    for rate in data:
        if rate['Cur_Abbreviation'] in currencies:
            rates[rate['Cur_Abbreviation']] = Decimal(str(rate['Cur_OfficialRate']))

    return JsonResponse(rates)


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
            print("Ошибка формы:", form.errors)  # Отладочное сообщение
    else:
        form = ExpenseForm()

    categories = Category.objects.all()
    expenses_today = Expense.objects.filter(user=request.user)
    total_expenses = expenses_today.aggregate(Sum('amount'))['amount__sum'] or 0

    context = {
        'form': form,
        'categories': categories,
        'expenses_today': expenses_today,
        'current_date': date.today(),
        'total_expenses': total_expenses
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


def expense_view(request, expense_id=None):
    if expense_id:
        expense = get_object_or_404(Expense, id=expense_id)
    else:
        expense = None

    if request.method == 'POST':
        form = ExpenseForm(request.POST, instance=expense)
        if form.is_valid():
            form.save()
            return redirect('expense_list')
    else:
        form = ExpenseForm(instance=expense)

    return render(request, 'homebuhweb/expenses/edit_expense.html', {'form': form, 'expense': expense})


def add_car_expense(request, expense_id):
    expense = Expense.objects.get(id=expense_id)

    if request.method == 'POST':
        form = CarExpenseForm(request.POST)

        if form.is_valid():
            car_expense = form.save(commit=False)
            car_expense.amount = expense.amount
            car_expense.date = expense.date
            car_expense.subsubcategory = expense
            car_expense.save()
            return redirect('user_cabinet')
    else:
        form = CarExpenseForm()

    return render(request, 'homebuhweb/expenses/add_car_expense.html', {'form': form, 'expense': expense})


def plan_expenses(request):
    expenses = PlannedExpense.objects.filter(user=request.user)
    return render(request, 'homebuhweb/expenses/plan_expenses.html', {'expenses': expenses})


def add_planned_expense(request):
    if request.method == 'POST':
        form = PlannedExpenseForm(request.POST)
        if form.is_valid():
            planned_expense = form.save(commit=False)
            planned_expense.user = request.user
            planned_expense.calculate_monthly_amount()
            planned_expense.save()
            return redirect('plan_expenses')
    else:
        form = PlannedExpenseForm()
    return render(request, 'homebuhweb/expenses/add_planned_expense.html', {'form': form})


def edit_planned_expense(request, pk):
    planned_expense = get_object_or_404(PlannedExpense, pk=pk, user=request.user)
    if request.method == 'POST':
        form = PlannedExpenseForm(request.POST, instance=planned_expense)
        if form.is_valid():
            planned_expense = form.save(commit=False)
            planned_expense.calculate_monthly_amount()
            planned_expense.save()
            return redirect('plan_expenses')
    else:
        form = PlannedExpenseForm(instance=planned_expense)
    return render(request, 'homebuhweb/expenses/edit_planned_expense.html', {'form': form})


def delete_planned_expense(request, pk):
    planned_expense = get_object_or_404(PlannedExpense, pk=pk, user=request.user)
    if request.method == 'POST':
        planned_expense.delete()
        return redirect('plan_expenses')
    return render(request, 'homebuhweb/expenses/delete_planned_expense.html', {'planned_expense': planned_expense})


def add_credit(request):
    if request.method == 'POST':
        form = CreditForm(request.POST)
        if form.is_valid():
            credit = form.save(commit=False)
            credit.user = request.user
            credit.save()

            # Выполнение расчетов
            principal_amount = credit.principal_amount
            monthly_interest = credit.monthly_interest
            monthly_payment = credit.monthly_payment

            # Вывод результатов расчетов
            return render(request, 'homebuhweb/credit/add_credit.html', {
                'form': form,
                'credits': Credit.objects.filter(user=request.user),
                'credit': None,
                'principal_amount': principal_amount,
                'monthly_interest': monthly_interest,
                'monthly_payment': monthly_payment,
            })
    else:
        form = CreditForm()

    credits = Credit.objects.filter(user=request.user)

    return render(request, 'homebuhweb/credit/add_credit.html', {'form': form, 'credits': credits, 'credit': None})


def edit_credit(request, pk):
    credit = get_object_or_404(Credit, pk=pk, user=request.user)

    if request.method == 'POST':
        form = CreditForm(request.POST, instance=credit)
        if form.is_valid():
            form.save()

            # Выполнение расчетов
            principal_amount = credit.principal_amount
            monthly_interest = credit.monthly_interest
            monthly_payment = credit.monthly_payment

            # Вывод результатов расчетов
            return render(request, 'homebuhweb/credit/add_credit.html', {
                'form': form,
                'credits': Credit.objects.filter(user=request.user),
                'credit': credit,
                'principal_amount': principal_amount,
                'monthly_interest': monthly_interest,
                'monthly_payment': monthly_payment,
            })
    else:
        form = CreditForm(instance=credit)

    credits = Credit.objects.filter(user=request.user)

    return render(request, 'homebuhweb/credit/add_credit.html', {'form': form, 'credits': credits, 'credit': credit})


def delete_credit(request):
    if request.method == 'POST':
        credit_id = request.POST.get('credit_id')
        credit = get_object_or_404(Credit, id=credit_id, user=request.user)
        credit.delete()
        return redirect('add_credit')

    return redirect('add_credit')


def show_grafics(request):
    return render(request, 'homebuhweb/diagrams/show_grafics.html')
