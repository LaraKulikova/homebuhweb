from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.shortcuts import render, redirect

from .forms import UserForm, ProfileForm


def homepage(request):
    return render(request, 'homebuhweb/homepage.html')


def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
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
    return render(request, 'homebuhweb/login/usercabinet.html')


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
def user_prof(request):
    if request.method == 'POST':
        user_form = UserForm(request.POST, instance=request.user)
        profile_form = ProfileForm(request.POST, request.FILES, instance=request.user.profile)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            return redirect('user_prof')
        else:
            return render(request, 'homebuhweb/login/user_prof.html', {
                'user_form': user_form,
                'profile_form': profile_form
            })
    else:
        user_form = UserForm(instance=request.user)
        profile_form = ProfileForm(instance=request.user.profile)
        return render(request, 'homebuhweb/login/user_prof.html', {
            'user_form': user_form,
            'profile_form': profile_form
        })


# def logout_view(request):
#     logout(request)
#     return redirect('login')
def delete_avatar(request):
    user = request.user
    user.profile.avatar.delete()  # Удаляем аватар
    return redirect('user_prof')  # Перенаправляем обратно на страницу профиля

