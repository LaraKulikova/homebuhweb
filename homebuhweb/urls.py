from django.urls import path
from . import views

urlpatterns = [
    path('', views.homepage, name='homepage'),
    path('login/', views.login_view, name='login'),
    path('check_user/', views.check_user, name='check_user'),
    path('usercabinet/', views.user_cabinet, name='user_cabinet'),
]