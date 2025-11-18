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


@login_required
def creating_request_view(request):
    if request.method == 'POST':
        form = RequestCreationForm(request.POST, request.FILES)
        if form.is_valid():
            request_obj = form.save(commit=False)
            request_obj.user = request.user
            request_obj.status = Status.objects.get(name="New")
            request_obj.save()
            return redirect('user_requests')
    else:
        form = RequestCreationForm()

    return render(request, 'catalog/create_request.html', {
        'form': form,
        'list_categories': Category.objects.all()
    })

@login_required
def deleting_request_view(request, pk):
    request_to_delete = get_object_or_404(Request, pk=pk)
    request_to_delete.delete()
    return redirect('user_requests')

@login_required
def user_request_list_view(request):
    request_user_list = Request.objects.filter(user=request.user)
    return render(request, 'catalog/user_request_list.html', {'request_list': request_user_list})