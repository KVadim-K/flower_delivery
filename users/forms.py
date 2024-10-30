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
        required=False,
        label='Номер телефона',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите номер телефона'
        })
    )
    address = forms.CharField(
        required=False,
        label='Адрес',
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'placeholder': 'Введите адрес',
            'rows': 3
        })
    )
    telegram_id = forms.CharField(
        required=False,
        label='Telegram ID',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите ваш Telegram ID'
        })
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'phone', 'address', 'telegram_id', 'password1', 'password2')

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('Пользователь с таким email уже существует.')
        return email

    def clean_telegram_id(self):
        telegram_id = self.cleaned_data.get('telegram_id')
        if telegram_id and User.objects.filter(telegram_id=telegram_id).exists():
            raise forms.ValidationError('Этот Telegram ID уже связан с другим пользователем.')
        return telegram_id
