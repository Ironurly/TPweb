from urllib import request
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from django.views import View
from django.contrib import auth
from webproject.mixins import AsideTagsView
from django.views.generic import FormView
from users.forms import LoginForm, SettingsForm, SignUpForm
from django.urls import reverse, reverse_lazy
from django.contrib.auth import logout
from django.contrib.auth.models import User

class LoginView(AsideTagsView, FormView):
    template_name = "webproject/login.html"
    form_class = LoginForm
    success_url = reverse_lazy('webproject:index_question_view')
    
    def form_valid(self, form):
        email = form.cleaned_data['email']
        password = form.cleaned_data['password']
        
        user = auth.authenticate(
            self.request, 
            username=email,
            password=password
        )
        if user:
            auth.login(self.request, user)
            return HttpResponseRedirect(reverse("users:settings"))
        
        form.add_error(None, "Неверный email или пароль")
        return self.form_invalid(form)

class SettingsView(AsideTagsView, FormView):
    template_name = "webproject/settings.html"
    form_class = SettingsForm
    success_url = reverse_lazy('webproject:index_question_view')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def get_initial(self):
        initial = super().get_initial()
        if self.request.user.is_authenticated:
            initial['email'] = self.request.user.email
            initial['nickname'] = self.request.user.first_name
        return initial
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            context['form_data'] = {
                'email': self.request.user.email,
                'nickname': self.request.user.first_name
            }
        return context

    def form_valid(self, form):
        user = self.request.user
        
        user.email = form.cleaned_data['email']
        user.username = form.cleaned_data['email']
        user.first_name = form.cleaned_data['nickname']
        
        password = form.cleaned_data['password']
        if password:
            user.set_password(password)
        
        user.save()
        
        if password:
            auth.login(self.request, user)
        
        return HttpResponseRedirect(self.success_url)

class SignUpView(AsideTagsView, FormView):
    template_name = "webproject/signup.html"
    form_class = SignUpForm
    success_url = reverse_lazy('webproject:index_question_view')

    def form_valid(self, form):
        email = form.cleaned_data['email']
        nickname = form.cleaned_data['nickname']
        password = form.cleaned_data['password']
        
        user = User.objects.create_user(
            username=email,
            email=email,
            first_name=nickname,
            password=password
        )
        
        user = auth.authenticate(
            self.request,
            username=email,
            password=password
        )
        
        if user:
            auth.login(self.request, user)
            return HttpResponseRedirect(reverse("users:settings"))
        
        return self.form_invalid(form)

class LogOut(View):
    def get(self, request, *args, **kwargs):
        logout(request)
        return redirect('webproject:index_question_view')
