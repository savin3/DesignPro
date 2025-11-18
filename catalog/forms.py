import re

from django.contrib.auth.forms import UserCreationForm
from django import forms
from django.core.exceptions import ValidationError

from catalog.models import AdvUser

class CustomUserCreationForm(UserCreationForm):
    last_name = forms.CharField(
        max_length=200,
        required=True,
        label='Фамилия',
        widget=forms.TextInput()
    )

    first_name = forms.CharField(
        max_length=200,
        required=True,
        label='Имя',
        widget=forms.TextInput()
    )

    patronymic = forms.CharField(
        max_length=200,
        required=True,
        label='Отчество',
        widget=forms.TextInput()
    )

    email = forms.EmailField(
        required=True,
        label='Email',
        widget=forms.EmailInput()
    )

    personal_data_agreement = forms.BooleanField(
        required=True,
        label='Я согласен на обработку персональных данных',
        widget=forms.CheckboxInput(),
        error_messages={'required': 'Вы должны согласиться на обработку персональных данных'}
    )

    class Meta:
        model = AdvUser
        fields = ('last_name', 'first_name', 'patronymic', 'username', 'email', 'password1', 'password2',
        'personal_data_agreement')

    def clean_last_name(self):
        last_name = self.cleaned_data.get('last_name')
        if not re.match(r'^[а-яА-ЯёЁ\s\-]+$', last_name):
            raise ValidationError(
                'Фамилия должна содержать только кириллические буквы, пробелы и дефис')
        return last_name

    def clean_first_name(self):
        first_name = self.cleaned_data.get('first_name')
        if not re.match(r'^[а-яА-ЯёЁ\s\-]+$', first_name):
            raise ValidationError('Имя должно содержать только кириллические буквы, пробелы и дефис')
        return first_name

    def clean_patronymic(self):
        patronymic = self.cleaned_data.get('patronymic')
        if not re.match(r'^[а-яА-ЯёЁ\s\-]+$', patronymic):
            raise ValidationError('Отчество должно содержать только кириллические буквы, пробелы и дефис')
        return patronymic

    def clean_username(self):
        username = self.cleaned_data.get('username')

        if not re.match(r'^[a-zA-Z\-]+$', username):
            raise ValidationError('Логин должен содержать только латинские буквы и дефис')

        if AdvUser.objects.filter(
                username=username).exists():  # Если у нас есть пользователь с текущим логином, то кидаем ошибку
            raise ValidationError('Пользователь с таким логином уже существует')

        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')

        if AdvUser.objects.filter(
                email=email).exists():  # Если у нас есть пользователь с текущим email, то кидаем ошибку
            raise ValidationError('Пользователь с таким email уже существует')
        return email

    def clean_personal_data_agreement(self):
        agreement = self.cleaned_data.get('personal_data_agreement')
        if not agreement:
            raise ValidationError('Вы должны согласиться на обработку персональных данных')
        return agreement


class RequestCreationForm(forms.ModelForm):
    description = forms.CharField(
        max_length=1000,
        required=True,
        label='Описание заявки',
        widget=forms.TextInput()
    )
    title = forms.CharField(
        max_length=200,
        required=True,
        label='Заголовок заявки',
        widget=forms.TextInput()
    )
    category = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        required=True,
        label='Категории',
        widget=forms.Select()
    )
    image = forms.ImageField(
        required=True,
        label='Изображение дизайна',
        widget=forms.FileInput(attrs={'accept': 'image/*'}),
        help_text='Допустимые форматы: JPG, JPEG, PNG, BMP. Максимальный размер: 2MB'
    )

    class Meta:
        model = Request
        fields = ['title', 'description', 'image', 'category']

    def clean_image(self):
        image = self.cleaned_data.get('image')
        self.validate_image_file(image)
        return image

    def validate_image_file(self, file):
        max_size = 2 * 1024 * 1024
        if file.size > max_size:
            raise ValidationError("Размер файла не должен превышать 2MB")

        valid_extensions = ['.jpg', '.jpeg', '.png', '.bmp']
        ext = os.path.splitext(file.name)[1].lower()
        if ext not in valid_extensions:
            raise ValidationError("Недопустимый формат файла. Разрешены: JPG, JPEG, PNG, BMP")