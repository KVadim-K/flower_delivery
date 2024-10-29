# orders/forms.py

from django import forms
import re

class OrderDeliveryForm(forms.Form):
    address = forms.CharField(
        max_length=255,
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'Введите адрес доставки'}),
        label='Адрес'
    )
    city = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'Введите город'}),
        label='Город'
    )
    postal_code = forms.CharField(
        max_length=20,
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'Введите почтовый индекс'}),
        label='Почтовый индекс'
    )
    phone_number = forms.CharField(
        max_length=20,
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'Введите номер телефона'}),
        label='Телефон'
    )

    def clean_phone_number(self):
        phone = self.cleaned_data.get('phone_number')
        # Определяем шаблон для номера телефона (например, +7XXXXXXXXXX или 8XXXXXXXXXX)
        pattern = re.compile(r'^(\+7|8)\d{10}$')
        if not pattern.match(phone):
            raise forms.ValidationError('Введите корректный номер телефона в формате +7XXXXXXXXXX или 8XXXXXXXXXX.')
        return phone

    def clean_postal_code(self):
        postal_code = self.cleaned_data.get('postal_code')
        # Предполагаем, что почтовый индекс состоит из 6 цифр (для России)
        pattern = re.compile(r'^\d{6}$')
        if not pattern.match(postal_code):
            raise forms.ValidationError('Почтовый индекс должен состоять из 6 цифр.')
        return postal_code

    def clean_city(self):
        city = self.cleaned_data.get('city')
        # Убедимся, что город содержит только буквы, пробелы и дефисы
        pattern = re.compile(r'^[A-Za-zА-Яа-яЁё\s-]+$')
        if not pattern.match(city):
            raise forms.ValidationError('Город может содержать только буквы, пробелы и дефисы.')
        return city

    def clean_address(self):
        address = self.cleaned_data.get('address')
        # Простая проверка: адрес должен содержать минимум улицу и номер дома
        if len(address.split()) < 2:
            raise forms.ValidationError('Пожалуйста, укажите полный адрес, включая улицу и номер дома.')
        return address
