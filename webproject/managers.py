from webproject.models import Question
from django.db.models import Q
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

class QuestionManager():

    def get_hot_questions(self):
        return Question.objects.all().filter(is_active=True).order_by('-likes')

    def get_new_questions(self):
        return Question.objects.all().filter(is_active=True).order_by('-created_at')
    
    def get_tagged_questions(self, tag):
        if not tag:
            questions = Question.objects.all()
        else:
            questions = Question.objects.all().filter(Q(tags__title = tag))
        
        return questions.filter(is_active=True).order_by("-created_at")
    
    def get_question_by_id(self, id):
        return Question.objects.filter(is_active=True).get(id=id)

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
    