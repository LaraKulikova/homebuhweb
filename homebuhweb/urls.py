from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.homepage, name='homepage'),
    path('login/', views.login_view, name='login'),
    path('check_user/', views.check_user, name='check_user'),
    path('usercabinet/', views.user_cabinet, name='user_cabinet'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
