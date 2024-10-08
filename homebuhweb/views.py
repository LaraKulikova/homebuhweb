from django.http import JsonResponse
from django.contrib.auth import authenticate, login
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
import json


def homepage(request):
    return render(request, 'homebuhweb/homepage.html')


@csrf_exempt
def check_user(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        username_or_email = data.get('usernameOrEmail')
        password = data.get('password')

        user = authenticate(request, username=username_or_email, password=password)
        if user is not None:
            login(request, user)
            return JsonResponse({'exists': True})
        else:
            return JsonResponse({'exists': False})


def login_view(request):
    return render(request, 'homebuhweb/login.html')


def user_cabinet(request):
    return render(request, 'homebuhweb/login/usercabinet.html')  # Добавьте это представление
