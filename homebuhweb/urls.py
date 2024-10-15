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
    path('user_prof/', views.user_prof, name='user_prof'),
    path('delete_avatar/', views.delete_avatar, name='delete_avatar'),
    path('logout/', auth_views.LogoutView.as_view(next_page='homepage'), name='logout'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)