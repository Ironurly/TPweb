from django import forms
from django.contrib.auth.models import User

class SettingsForm(forms.Form):
    email = forms.EmailField(required=True)
    nickname = forms.CharField(required=True, min_length=3)
    password = forms.CharField(required=True, min_length=8, widget=forms.PasswordInput)
    password_r = forms.CharField(required=True, widget=forms.PasswordInput)

    def clean_email(self):
        email = self.cleaned_data.get("email")

        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Email is already registered")

        return email

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        password_r = cleaned_data.get("password_r")

        if password and password_r and password != password_r:
            raise forms.ValidationError("Passwords do not match")

        return cleaned_data

class SignUpForm(forms.Form):
    email = forms.EmailField(required=True)
    nickname = forms.CharField(required=True, min_length=3)
    password = forms.CharField(required=True, min_length=8)
    password_r = forms.CharField(required=True)

    def clean_email(self):
        email = self.cleaned_data.get("email")

        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Email is already registered")

        return email

    def clean(self):
        cleaned = super().clean()
        pw = cleaned.get("password")
        pw_r = cleaned.get("password_r")

        if pw and pw_r and pw != pw_r:
            raise forms.ValidationError("Passwords do not match")

        return cleaned