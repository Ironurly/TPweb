from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import TemplateView
from django.views.generic import FormView

from webproject.forms import SettingsForm
from webproject.managers import QuestionManager, get_paginator_page
from webproject.mixins import AsideTagsView
from webproject.models import Question

class IndexQuestionView(AsideTagsView, TemplateView):
    template_name = "webproject/index.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        questions = QuestionManager().get_new_questions()
        get_paginator_page(self.request, questions, context, per_page=5)

        context['meta'] = {
            'page_name':'main',
        }

        return context

    def dispatch(self, request, *args, **kwargs):
        return super(IndexQuestionView, self).dispatch(request, *args, **kwargs)

class HotQuestionView(AsideTagsView, TemplateView):
    template_name = "webproject/index.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        questions = QuestionManager().get_hot_questions()
        get_paginator_page(self.request, questions, context, per_page=5)
        
        context['meta'] = {
            'page_name':'hot',
        }

        return context

    def dispatch(self, request, *args, **kwargs):
        return super(HotQuestionView, self).dispatch(request, *args, **kwargs)


class DetailView(AsideTagsView, TemplateView):
    template_name = "webproject/question.html"
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        questions = get_object_or_404(Question, pk=self.kwargs.get("pk"))
        comments = questions.comments.filter(is_active=True).order_by('-created_at')
        get_paginator_page(self.request, comments, context, per_page=5)
        
        context["question"] = questions

        return context


class AskView(AsideTagsView, TemplateView):
    template_name = "webproject/ask.html"
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        return context

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
    
    def email_exists(self, email):
        existing_emails = ['existing@example.com', 'test@test.com']
        return email in existing_emails

class SignUpView(AsideTagsView, TemplateView):
    template_name = "webproject/signup.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        errors = self.request.session.pop('signup_errors', None)
        form_data = self.request.session.pop('form_data', {})
        
        context['errors'] = errors if errors else []
        context['form_data'] = form_data
        
        return context

    def post(self, request, *args, **kwargs):
        errors = []
        form_data = {
            'email': request.POST.get('email', '').strip(),
            'nickname': request.POST.get('nickname', '').strip(),
        }

        email = form_data['email']
        if not email:
            errors.append('Email is required')

        nickname = form_data['nickname']
        if not nickname:
            errors.append('Nickname is required')
        elif len(nickname) < 3:
            errors.append('Nickname is too short (minimum 3 characters)')

        password = request.POST.get('password', '').strip()
        password_r = request.POST.get('password_r', '').strip()
        
        if not password:
            errors.append('Password is required')
        elif password != password_r:
            errors.append('Passwords do not match')

        if email and self.email_exists(email):
            errors.append('Email is already registered')

        if errors:
            request.session['signup_errors'] = errors
            request.session['form_data'] = form_data
            return self.get(request, *args, **kwargs)
        else:
            if 'signup_errors' in request.session:
                del request.session['signup_errors']
            if 'form_data' in request.session:
                del request.session['form_data']
                
            return redirect('webproject:login')

    def email_exists(self, email):
        existing_emails = ['existing@example.com', 'test@test.com']
        return email in existing_emails

class TagView(AsideTagsView, TemplateView):
    template_name = "webproject/tag.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        tag_name = self.kwargs.get('tag_name')
        questions = QuestionManager().get_tagged_questions(tag_name)

        get_paginator_page(self.request, questions, context, per_page=5)

        context["tag_name"] = tag_name
        
        return context