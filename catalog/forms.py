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