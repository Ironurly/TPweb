from django.shortcuts import get_object_or_404
from django.views.generic import TemplateView, DetailView
from webproject.managers import QuestionManager, get_paginator_page
from webproject.mixins import AsideTagsView
from webproject.models import Question, Tag

class IndexQuestionView(AsideTagsView, TemplateView):
    template_name = "webproject/index.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        manager = QuestionManager()
        questions = manager.get_new_questions()
        get_paginator_page(self.request, questions, context, per_page=5)

        context['meta'] = {
            'page_name':'main',
        }

        return context

class HotQuestionView(AsideTagsView, TemplateView):
    template_name = "webproject/index.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        manager = QuestionManager()
        questions = manager.get_hot_questions()
        get_paginator_page(self.request, questions, context, per_page=5)
        
        context['meta'] = {
            'page_name':'hot',
        }

        return context

class QuestionDetailView(AsideTagsView, DetailView):
    template_name = "webproject/question.html"

    queryset = Question.objects.filter(is_active=True)
    
    def get_queryset(self):
        return super().get_queryset().select_related('author').prefetch_related('tags')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        question = self.object
        answers = question.answers.filter(is_active=True).select_related('author').order_by('-created_at')
        get_paginator_page(self.request, answers, context, per_page=5)
        
        context["question"] = question

        return context


class AskView(AsideTagsView, TemplateView):
    template_name = "webproject/ask.html"
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        return context

class TagView(AsideTagsView, TemplateView):
    template_name = "webproject/tag.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        manager = QuestionManager()
        tag_name = self.kwargs.get('tag_name')
        tag = get_object_or_404(Tag, title=tag_name)
        questions = manager.get_tagged_questions(tag.id)

        get_paginator_page(self.request, questions, context, per_page=5)

        context["tag_name"] = tag_name
        
        return context