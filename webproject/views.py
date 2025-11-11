from django.shortcuts import redirect, render
from django.views import View
from django.views.generic import TemplateView
from rest_framework.generics import RetrieveAPIView
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
# Create your views here.

def index_view(request):
    questions = []
    for i in range(0, 50):
        questions.append({
            "id": i,
            "text": f"Question {i}",
            "description": "Guys, i have trouble with a moon park. Can't find the black-jack...",
            "tags": ["black-jack", "bender"],
            "likes": i+2
        })
    
    page_number = request.GET.get("page", 1)
    paginator = Paginator(questions, per_page=5)
    
    try:
        page_obj = paginator.page(page_number)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)

    return render(request, "webproject/index.html", {
        "object_list": page_obj.object_list,
        "page_obj": page_obj,
        "paginator": paginator
    })
ANSWERS = [
    {
        "id": 1,
        "text": "Emmmmm...."
    },
    {
        "id": 2,
        "text": "Emmmmm...."
    },
]
class DetailView(TemplateView):
    template_name = "webproject/question.html"
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        page_number = self.request.GET.get("page", 1)
        paginator = Paginator(ANSWERS, per_page=5)
        try:
            page_obj = paginator.page(page_number)
        except PageNotAnInteger:
            page_obj = paginator.page(1)
        except EmptyPage:
            page_obj = paginator.page(paginator.num_pages)

        context.update({
            "object_list": page_obj.object_list,
            "page_obj": page_obj,
            "paginator": paginator
        })
        return context


class AskView(TemplateView):
    template_name = "webproject/ask.html"

class LoginView(TemplateView):
    template_name = "webproject/login.html"

class SettingsView(TemplateView):
    template_name = "webproject/settings.html"
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

class SignUpView(TemplateView):
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

class TagView(TemplateView):
    template_name = "webproject/tag.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        tag_name = self.kwargs.get('tag_name')
        
        tags = []
        for i in range(0, 20):
            tags.append({
                "id": i,
                "text": "Tag",
            })
        
        page_number = self.request.GET.get("page", 1)
        paginator = Paginator(tags, per_page=5)
        
        try:
            page_obj = paginator.page(page_number)
        except PageNotAnInteger:
            page_obj = paginator.page(1)
        except EmptyPage:
            page_obj = paginator.page(paginator.num_pages)
        
        context.update({
            "object_list": page_obj.object_list,
            "page_obj": page_obj,
            "paginator": paginator,
            "tag_name": tag_name
        })
        
        return context