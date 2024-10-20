from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.homepage, name='homepage'),
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('user_cabinet/', views.user_cabinet, name='user_cabinet'),
path('api/currency-rates/', views.get_currency_rates, name='currency_rates'),
    path('user_prof/', views.user_prof, name='user_prof'),
    path('delete_avatar/', views.delete_avatar, name='delete_avatar'),
    path('logout/', auth_views.LogoutView.as_view(next_page='homepage'), name='logout'),
    path('incomes/add/', views.add_income, name='add_income'),
    path('incomes/edit/<int:id>/', views.add_income, name='edit_income'),
    path('incomes/delete/<int:id>/', views.delete_income, name='delete_income'),
    path('expenses/add/', views.add_expense, name='add_expense'),
    path('expenses/edit/<int:expense_id>/', views.edit_expense, name='edit_expense'),
    path('get_subcategories/<int:category_id>/', views.get_subcategories, name='get_subcategories'),
    path('get_subsubcategories/<int:subcategory_id>/', views.get_subsubcategories, name='get_subsubcategories'),
    path('expenses/delete/<int:expense_id>/', views.delete_expense, name='delete_expense'),
    path('add_car_expense/<int:expense_id>/', views.add_car_expense, name='add_car_expense'),
    path('plan_expenses/', views.plan_expenses, name='plan_expenses'),
    path('add_planned_expense.html/', views.add_planned_expense, name='add_planned_expense'),
    path('edit_planned_expense/<int:pk>/', views.edit_planned_expense, name='edit_planned_expense'),
    path('delete_planned_expense/<int:pk>/', views.delete_planned_expense, name='delete_planned_expense'),
    path('add_credit/', views.add_credit, name='add_credit'),
    path('edit_credit/<int:pk>/', views.edit_credit, name='edit_credit'),
    path('delete_credit/<int:pk>/', views.delete_credit, name='delete_credit'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)