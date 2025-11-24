from django.http import Http404
from webproject.models import Question, Tag
from django.db.models import Q
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

class QuestionManager():

    def get_hot_questions(self):
        return Question.objects.filter(is_active=True) \
            .select_related('author') \
            .prefetch_related('tags') \
            .order_by('-likes')

    def get_new_questions(self):
        return Question.objects.filter(is_active=True) \
            .select_related('author') \
            .prefetch_related('tags') \
            .order_by('-created_at')
    
    def get_tagged_questions(self, tag_id):
        
        return Question.objects.filter(
            tags__id=tag_id,
            is_active=True
        ).select_related('author') \
         .prefetch_related('tags') \
         .order_by("-created_at")
    
    def get_question_by_id(self, id):
        return Question.objects.filter(is_active=True) \
            .select_related('author') \
            .prefetch_related('tags') \
            .get(id=id)

def get_paginator_page(request, instance_list, context ,per_page=5):
    
    page_number = request.GET.get("page", 1)
    paginator = Paginator(instance_list, per_page=per_page)

    try:
        page_obj = paginator.page(page_number)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)
    
    context["object_list"] = page_obj.object_list
    context["page_obj"] = page_obj
    context["paginator"] = paginator
    