from django import forms
from django.contrib.auth.models import User

class LoginForm(forms.Form):
    email = forms.CharField(max_length=255, required=True)
    password = forms.CharField(max_length=255, required=True)

class SettingsForm(forms.Form):
    email = forms.EmailField(required=True)
    nickname = forms.CharField(required=True, min_length=3)
    password = forms.CharField(required=False, min_length=8, widget=forms.PasswordInput)
    password_r = forms.CharField(required=False, widget=forms.PasswordInput)

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get("email")
        password = cleaned_data.get("password")
        password_r = cleaned_data.get("password_r")

        if email and User.objects.filter(email=email).exclude(pk=self.user.pk if self.user else None).exists():
            raise forms.ValidationError("Email is already registered")

        if password or password_r:
            if password != password_r:
                raise forms.ValidationError("Passwords do not match")
            elif password and len(password) < 8:
                raise forms.ValidationError("Password must be at least 8 characters")

        return cleaned_data

class SignUpForm(forms.Form):
    email = forms.EmailField(required=True)
    nickname = forms.CharField(required=True, min_length=3)
    password = forms.CharField(required=True, min_length=8, widget=forms.PasswordInput)
    password_r = forms.CharField(required=True, widget=forms.PasswordInput)

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get("email")
        nickname = cleaned_data.get("nickname")
        password = cleaned_data.get("password")
        password_r = cleaned_data.get("password_r")

        if email and User.objects.filter(email=email).exists():
            raise forms.ValidationError("Email is already registered")
        
        if nickname and User.objects.filter(first_name=nickname).exists():
            raise forms.ValidationError("Nickname is already taken")

        if password and password_r and password != password_r:
            raise forms.ValidationError("Passwords do not match")

        return cleaned_data