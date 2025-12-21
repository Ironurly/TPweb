from django.shortcuts import get_object_or_404, redirect
from django.views.generic import TemplateView, DetailView, FormView
from django.views import View
from django.urls import reverse_lazy
from webproject.mixins import AsideTagsView
from webproject.models import Question, Tag, Answer, get_paginator_page
from webproject.forms import AnswerForm, AskQuestionForm

class IndexQuestionView(AsideTagsView, TemplateView):
    template_name = "webproject/index.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        questions = Question.objects.get_new_questions()
        get_paginator_page(self.request, questions, context, per_page=5)

        context['meta'] = {
            'page_name':'main',
        }

        return context

class HotQuestionView(AsideTagsView, TemplateView):
    template_name = "webproject/index.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        questions = Question.objects.get_hot_questions()
        get_paginator_page(self.request, questions, context, per_page=5)
        
        context['meta'] = {
            'page_name':'hot',
        }

        return context

class QuestionDetailView(AsideTagsView, FormView):
    template_name = "webproject/question.html"
    form_class = AnswerForm
    
    def get_question(self):
        question_id = self.kwargs.get('pk')
        return get_object_or_404(
            Question.objects
            .filter(is_active=True)
            .select_related('author')
            .prefetch_related('tags'),
            pk=question_id
        )
    
    def post(self, request, *args, **kwargs):
        answer_pk = request.POST.get('answer_pk')
        if answer_pk:
            return self.mark_correct_answer(answer_pk)
        
        return super().post(request, *args, **kwargs)
    
    def mark_correct_answer(self, answer_pk):
        if not self.request.user.is_authenticated:
            return redirect('users:login')
        
        question = self.get_question()
        answer = get_object_or_404(Answer, pk=answer_pk, question=question, is_active=True)
        
        if question.author != self.request.user:
            return redirect('webproject:question_detail', pk=question.id)
        
        answer.is_correct = not answer.is_correct
        answer.save()
        
        return redirect('webproject:question_detail', pk=question.id)
    
    def form_valid(self, form):
        if not self.request.user.is_authenticated:
            return redirect('users:login')
        
        question = self.get_question()
        
        question.answers.create(
            body=form.cleaned_data['text'],
            author=self.request.user
        )
        
        question.answer()
        
        return redirect('webproject:question_detail', pk=question.id)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        question = self.get_question()
        answers = question.answers.filter(is_active=True).select_related('author').order_by('-created_at')
        get_paginator_page(self.request, answers, context, per_page=5)
        
        context["question"] = question

        return context


class AskView(AsideTagsView, FormView):
    template_name = "webproject/ask.html"
    form_class = AskQuestionForm
    success_url = reverse_lazy('webproject:index_question_view')

    def form_valid(self, form):
        if not self.request.user.is_authenticated:
            return redirect('users:login')
        
        question = Question.objects.create(
            title=form.cleaned_data['title'],
            body=form.cleaned_data['text'],
            author=self.request.user
        )
        
        tag_names = form.cleaned_data.get('tags', [])
        for tag_name in tag_names:
            tag, _ = Tag.objects.get_or_create(title=tag_name)
            question.tags.add(tag)
        
        return redirect('webproject:question_detail', pk=question.id)

class TagView(AsideTagsView, TemplateView):
    template_name = "webproject/tag.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        tag_name = self.kwargs.get('tag_name')
        tag = get_object_or_404(Tag, title=tag_name)
        questions = Question.objects.get_tagged_questions(tag.id)

        get_paginator_page(self.request, questions, context, per_page=5)

        context["tag_name"] = tag_name
        
        return context