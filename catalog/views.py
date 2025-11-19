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
    in_work_status = Status.objects.get(name="In_work")
    requests_in_work_count = Request.objects.filter(status=in_work_status).count()
    done_status = Status.objects.get(name="Done")
    latest_completed_request_list = Request.objects.filter(
        status=done_status
    ).order_by('-pub_date')[:4]

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

    status_filter = request.GET.get('status', 'all')

    if status_filter == 'new':
        filtered_requests = request_user_list.filter(status__name="New")
    elif status_filter == 'in_work':
        filtered_requests = request_user_list.filter(status__name="In_work")
    elif status_filter == 'done':
        filtered_requests = request_user_list.filter(status__name="Done")
    else:
        filtered_requests = request_user_list
    return render(request, 'catalog/user_requests.html', {
        'filtered_requests': filtered_requests,
        'current_filter': status_filter,
    })

@login_required
def profile_view(request):
    return render(request, 'catalog/profile.html')



@login_required
def admin_panel_include_all_requests_view(request):
    all_request_list = Request.objects.all()
    return render(request, 'catalog/admin_panel.html', {'all_request_list':all_request_list})

@login_required
@permission_required('catalog.moderator_access')
def category_view(request):
    if request.method == 'POST':
        form = CategoryCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('category')
    else:
        form = CategoryCreationForm()

    list_categories = Category.objects.all()
    return render(request, 'catalog/category.html', {
        'list_categories': list_categories,
        'form': form
    })

@login_required
def deleting_category_view(request, pk):
    category_to_delete = get_object_or_404(Category, pk=pk)
    category_to_delete.delete()
    return redirect('category')

@login_required
@permission_required('catalog.moderator_access')
def edit_request_view(request, pk):
    changeable_request = get_object_or_404(Request, pk=pk)

    if request.method == 'POST':
        if 'edit_category' in request.POST:
            category_id = request.POST.get('category')
            changeable_request.category = Category.objects.get(id=category_id)
            changeable_request.save()
            return redirect('admin_panel')

        elif 'edit_status_to_in_work' in request.POST:
            worker_comment = request.POST.get('worker_comment')
            completed_image = request.FILES.get('completed_image')

            if completed_image:
                try:
                    validate_image_file(completed_image)
                except ValidationError as e:
                    form = RequestEditForm(instance=changeable_request)
                    list_categories = Category.objects.all()
                    return render(request, 'catalog/edit_request.html', {
                        'changeable_request': changeable_request,
                        'list_categories': list_categories,
                        'form': form,
                        'error': str(e)
                    })
            changeable_request.status = Status.objects.get(name="In_work")

            changeable_request.worker_comment = worker_comment
            if completed_image:
                changeable_request.completed_image = completed_image

            changeable_request.save()
            return redirect('admin_panel')

        elif 'edit_status_to_done' in request.POST:
            worker_comment = request.POST.get('worker_comment')
            completed_image = request.FILES.get('completed_image')

            if completed_image:
                try:
                    validate_image_file(completed_image)
                except ValidationError as e:
                    form = RequestEditForm(instance=changeable_request)
                    list_categories = Category.objects.all()
                    return render(request, 'catalog/edit_request.html', {
                        'changeable_request': changeable_request,
                        'list_categories': list_categories,
                        'form': form,
                        'error': str(e)
                    })

            changeable_request.status = Status.objects.get(name="Done")

            changeable_request.worker_comment = worker_comment
            if completed_image:
                changeable_request.completed_image = completed_image

            changeable_request.save()
            return redirect('admin_panel')

    form = RequestEditForm(instance=changeable_request)
    list_categories = Category.objects.all()

    return render(request, 'catalog/edit_request.html', {
        'changeable_request': changeable_request,
        'list_categories': list_categories,
        'form': form,
    })


def validate_image_file(file):
    max_size = 2 * 1024 * 1024
    if file.size > max_size:
        raise ValidationError("Размер файла не должен превышать 2MB")

    valid_extensions = ['.jpg', '.jpeg', '.png', '.bmp']
    ext = os.path.splitext(file.name)[1].lower()
    if ext not in valid_extensions:
        raise ValidationError("Недопустимый формат файла. Разрешены: JPG, JPEG, PNG, BMP")