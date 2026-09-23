from django import forms
from django.contrib.auth.models import User, Group
from django.contrib.auth.password_validation import validate_password

from django.core.exceptions import ValidationError
import re

class UserRegistrationForm(forms.ModelForm):
    phone_number = forms.CharField(max_length=10, label="Phone Number (10 digits)")
    password = forms.CharField(widget=forms.PasswordInput, help_text="Min 8 characters, at least one letter and one number.")
    password_confirm = forms.CharField(widget=forms.PasswordInput, label="Confirm Password")

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']

    def clean_phone_number(self):
        phone = self.cleaned_data.get('phone_number')
        if not re.match(r'^\d{10}$', phone):
            raise ValidationError("Phone number must be exactly 10 digits.")
        return phone

    def clean_email(self):
        email = self.cleaned_data.get('email')
        allowed_domains = ['gmail.com', 'gov.in']
        domain = email.split('@')[-1]
        if domain not in allowed_domains:
            raise ValidationError(f"Email domain must be one of: {', '.join(allowed_domains)}")
        return email

    def clean_password(self):
        password = self.cleaned_data.get('password')
        if len(password) < 8:
            raise ValidationError("Password must be at least 8 characters long.")
        if not any(char.isdigit() for char in password):
            raise ValidationError("Password must contain at least one number.")
        if not any(char.isalpha() for char in password):
            raise ValidationError("Password must contain at least one letter.")
        return password

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data.get("password") != cleaned_data.get("password_confirm"):
            self.add_error('password_confirm', "Passwords do not match")
        return cleaned_data


class ManualPasswordResetForm(forms.Form):
    identifier = forms.CharField(
        max_length=150,
        label="Username or email",
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-3 rounded-2xl border border-slate-200 bg-white focus:ring-2 focus:ring-brand-500 focus:border-brand-500 transition-all outline-none',
            'placeholder': 'Username or email',
        })
    )
    new_password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-4 py-3 rounded-2xl border border-slate-200 bg-white focus:ring-2 focus:ring-brand-500 focus:border-brand-500 transition-all outline-none',
            'placeholder': 'New password',
        }),
        label="New password"
    )
    new_password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-4 py-3 rounded-2xl border border-slate-200 bg-white focus:ring-2 focus:ring-brand-500 focus:border-brand-500 transition-all outline-none',
            'placeholder': 'Confirm new password',
        }),
        label="Confirm new password"
    )

    def clean_identifier(self):
        identifier = self.cleaned_data.get('identifier', '').strip()
        if not identifier:
            raise ValidationError("Please enter your username or email.")

        user = User.objects.filter(username__iexact=identifier).first()
        if not user:
            user = User.objects.filter(email__iexact=identifier).first()

        if not user:
            raise ValidationError("No account was found with that username or email.")

        self.user = user
        return identifier

    def clean_new_password1(self):
        password = self.cleaned_data.get('new_password1')
        if password:
            try:
                validate_password(password)
            except ValidationError as exc:
                raise ValidationError(exc.messages)
        return password

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get('new_password1')
        password2 = cleaned_data.get('new_password2')
        if password1 and password2 and password1 != password2:
            self.add_error('new_password2', "Passwords do not match")
        return cleaned_data
