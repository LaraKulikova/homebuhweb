import base64
import datetime
import io
import urllib
import urllib.parse
from datetime import date, timedelta
from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP
from django.contrib import messages
import matplotlib.pyplot as plt
import pandas as pd
import requests
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import Group
from django.db.models import Sum
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.shortcuts import render
from django.templatetags.static import static

from .forms import CreditForm
from .forms import ExpenseForm, CarExpenseForm
from .forms import PlannedExpenseForm
from .forms import UserForm, ProfileForm
from .models import Category, SubCategory, SubSubCategory
from .models import Credit
from .models import Expense
from .models import Income, Profile
from .models import PlannedExpense
import textwrap


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
            messages.error(request, "Такого пользователя не существует или неверный пароль.")
            return redirect('homepage')
    else:
        form = AuthenticationForm()
        return render(request, 'homebuhweb/homepage.html', {'form': form})


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
    expenses = PlannedExpense.objects.filter(user=request.user)
    total_monthly_amount = Decimal('0.00')
    for expense in expenses:
        total_monthly_amount += expense.calculate_monthly_amount()
    total_monthly_amount = total_monthly_amount.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

    return render(request, 'homebuhweb/login/usercabinet.html', {
        'start_date': start_date,
        'end_date': end_date,
        'total_income': total_income,
        'total_income_usd': total_income_usd,
        'total_income_eur': total_income_eur,
        'total_income_rub': total_income_rub,
        'total_expenses': total_expenses,
        'total_monthly_amount': total_monthly_amount,
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
    total_monthly_amount = Decimal('0.00')
    for expense in expenses:
        total_monthly_amount += expense.calculate_monthly_amount()
        total_monthly_amount = total_monthly_amount.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    return render(request, 'homebuhweb/expenses/plan_expenses.html', {
                    'expenses': expenses,
                    'total_monthly_amount': total_monthly_amount })

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


@login_required
def show_grafics(request):
    # Получаем дату три месяца назад для расходов
    three_months_ago = date.today() - timedelta(days=90)
    # Получаем дату шесть месяцев назад для доходов
    six_months_ago = date.today() - timedelta(days=180)

    # Получаем расходы за последние три месяца
    expenses = Expense.objects.filter(user=request.user, date__gte=three_months_ago)
    # Получаем доходы за последние шесть месяцев
    incomes = Income.objects.filter(user=request.user, date__gte=six_months_ago)

    context = {}

    # Проверка наличия расходов
    if expenses.exists():
        # Группируем расходы по подподкатегориям и суммируем их
        expenses_by_subsubcategory = expenses.values('subsubcategory__name').annotate(total=Sum('amount'))
        # Преобразуем данные в DataFrame
        df_expenses = pd.DataFrame(list(expenses_by_subsubcategory))
        # Убедитесь, что столбец 'total' является числовым
        df_expenses['total'] = pd.to_numeric(df_expenses['total'], errors='coerce')
        # Создаем круговой график для расходов
        fig_expenses, ax_expenses = plt.subplots()
        wedges, texts, autotexts = ax_expenses.pie(
            df_expenses['total'],
            labels=df_expenses['subsubcategory__name'],
            autopct='%1.1f%%',
            startangle=90,
            textprops={'fontsize': 8}
        )
        ax_expenses.set_ylabel('')
        # Вручную вставляем символы новой строки и уменьшаем размер шрифта заголовка
        title_expenses = 'Процентное отношение расходов\nпо категориям по отношению\nк общему расходу'
        ax_expenses.set_title(title_expenses, fontsize=10)
        # Уменьшаем размер шрифта подписей
        plt.setp(autotexts, size=8, weight="bold")
        # Перенос длинных надписей
        for text in texts:
            text.set_text(textwrap.fill(text.get_text(), width=10))
        # Сохраняем график в буфер
        buf_expenses = io.BytesIO()
        plt.savefig(buf_expenses, format='png')
        buf_expenses.seek(0)
        string_expenses = base64.b64encode(buf_expenses.read())
        uri_expenses = urllib.parse.quote(string_expenses)
        context['data_expenses'] = uri_expenses
    else:
        context['message_expenses'] = 'У Вас пока нет расходов'

    # Проверка наличия доходов
    if incomes.exists():
        # Группируем доходы по типам и суммируем их
        incomes_by_type = incomes.values('income_type').annotate(total=Sum('amount'))
        # Преобразуем данные в DataFrame
        df_incomes = pd.DataFrame(list(incomes_by_type))
        # Убедитесь, что столбец 'total' является числовым
        df_incomes['total'] = pd.to_numeric(df_incomes['total'], errors='coerce')
        # Создаем круговой график для доходов
        fig_incomes, ax_incomes = plt.subplots()
        wedges, texts, autotexts = ax_incomes.pie(
            df_incomes['total'],
            labels=df_incomes['income_type'],
            autopct='%1.1f%%',
            startangle=90,
            textprops={'fontsize': 8}
        )
        ax_incomes.set_ylabel('')
        # Вручную вставляем символы новой строки и уменьшаем размер шрифта заголовка
        title_incomes = 'Процентное отношение доходов\nпо категориям по отношению\nк общему доходу'
        ax_incomes.set_title(title_incomes, fontsize=10)
        # Уменьшаем размер шрифта подписей
        plt.setp(autotexts, size=8, weight="bold")
        # Перенос длинных надписей
        for text in texts:
            text.set_text(textwrap.fill(text.get_text(), width=10))
        # Сохраняем график в буфер
        buf_incomes = io.BytesIO()
        plt.savefig(buf_incomes, format='png')
        buf_incomes.seek(0)
        string_incomes = base64.b64encode(buf_incomes.read())
        uri_incomes = urllib.parse.quote(string_incomes)
        context['data_incomes'] = uri_incomes
    else:
        context['message_incomes'] = 'У Вас пока нет доходов'

    return render(request, 'homebuhweb/diagrams/show_grafics.html', context)



