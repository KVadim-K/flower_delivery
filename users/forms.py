# users/forms.py

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model

User = get_user_model()

class RegistrationForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        label='Электронная почта',
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите электронную почту'
        })
    )
    phone = forms.CharField(
        required=True,  # Сделаем обязательным, если необходимо
        label='Номер телефона',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите номер телефона'
        })
    )
    # Удаляем поле 'address'

    class Meta:
        model = User
        fields = ('username', 'email', 'phone', 'password1', 'password2')

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('Пользователь с таким email уже существует.')
        return email

    # Удаляем метод clean_telegram_id, так как поле отсутствует в форме
