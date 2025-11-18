from django.contrib.auth import logout, authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Permission
from django.shortcuts import render, redirect, get_object_or_404
from .forms import CustomUserCreationForm, RequestCreationForm
from .models import Status, Category, Request


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
    try:
        in_work_status = Status.objects.get(name="In_work")
        requests_in_work_count = Request.objects.filter(status=in_work_status).count()
        done_status = Status.objects.get(name="Done")
        latest_completed_request_list = Request.objects.filter(
            status=done_status
        ).order_by('-pub_date')[:4]

    except Status.DoesNotExist:
        latest_completed_request_list = Request.objects.none()
        requests_in_work_count = 0

    return render(request, 'catalog/index.html', {'latest_completed_request_list': latest_completed_request_list, 'requests_in_work_count': requests_in_work_count})


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
def user_requests_view(request):
    request_user_list = Request.objects.filter(user=request.user)
    return render(request, 'catalog/user_requests.html', {'request_list': request_user_list})