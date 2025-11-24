from webproject.mixins import AsideTagsView
from django.views.generic import TemplateView
from django.views.generic import FormView
from users.forms import SettingsForm, SignUpForm
from django.urls import reverse_lazy

class LoginView(AsideTagsView, TemplateView):
    template_name = "webproject/login.html"
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        return context

class SettingsView(AsideTagsView, FormView):
    template_name = "webproject/settings.html"
    form_class = SettingsForm
    success_url = reverse_lazy('webproject:index_question_view')

    def form_valid(self, form):
        return super().form_valid(form)

class SignUpView(AsideTagsView, FormView):
    template_name = "webproject/signup.html"
    form_class = SignUpForm
    success_url = reverse_lazy('webproject:index_question_view')

    def form_valid(self, form):
        return super().form_valid(form)