from django.contrib.auth import logout, authenticate, login
from django.contrib.auth.models import Permission
from django.shortcuts import render, redirect
from .forms import CustomUserCreationForm


from django.shortcuts import render

def register_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password1'])
            user.save()

            login(request, user)
            return redirect('index')
    else:
        form = CustomUserCreationForm()

    return render(request, 'catalog/register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('index')

        return render(request, 'catalog/login.html', {'error': 'Неверное имя пользователя или пароль'})

    return render(request, 'catalog/login.html')

def logout_view(request):
    logout(request)
    return redirect('index')

def index_view(request):
    return render(request, 'catalog/index.html')