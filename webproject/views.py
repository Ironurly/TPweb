from django.shortcuts import get_object_or_404, redirect
from django.views.generic import TemplateView, FormView
from django.urls import reverse_lazy
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_protect
from webproject.mixins import AsideTagsView
from webproject.models import Question, Tag, Answer, QuestionLikes, AnswerLikes, get_paginator_page
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

        if self.request.user.is_authenticated:
            question_ids = [q.id for q in context['object_list']]
            question_votes = QuestionLikes.objects.filter(
                user=self.request.user,
                question_id__in=question_ids
            ).values('question_id', 'reaction')
            votes_dict = {vote['question_id']: vote['reaction'] for vote in question_votes}
            
            for question in context['object_list']:
                question.user_vote = votes_dict.get(question.id)
        else:
            for question in context['object_list']:
                question.user_vote = None

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

        if self.request.user.is_authenticated:
            question_ids = [q.id for q in context['object_list']]
            question_votes = QuestionLikes.objects.filter(
                user=self.request.user,
                question_id__in=question_ids
            ).values('question_id', 'reaction')
            votes_dict = {vote['question_id']: vote['reaction'] for vote in question_votes}
            
            for question in context['object_list']:
                question.user_vote = votes_dict.get(question.id)
        else:
            for question in context['object_list']:
                question.user_vote = None

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
        
        if self.request.user.is_authenticated:
            question_vote = QuestionLikes.objects.filter(
                user=self.request.user, 
                question=question
            ).first()
            context['user_question_vote'] = question_vote.reaction if question_vote else None
            
            answer_ids = [answer.id for answer in context['object_list']]
            answer_votes = AnswerLikes.objects.filter(
                user=self.request.user,
                answer_id__in=answer_ids
            ).values('answer_id', 'reaction')
            votes_dict = {vote['answer_id']: vote['reaction'] for vote in answer_votes}
            
            for answer in context['object_list']:
                answer.user_vote = votes_dict.get(answer.id)
        else:
            context['user_question_vote'] = None
            for answer in context['object_list']:
                answer.user_vote = None

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

@require_POST
@csrf_protect
def vote_question(request):
    if not request.user.is_authenticated:
        return JsonResponse({'status': 'error', 'message': 'Authentication required'}, status=401)
    
    question_id = request.POST.get('question_id')
    vote_type = request.POST.get('vote_type')
    
    if not question_id or vote_type not in ['like', 'dislike']:
        return JsonResponse({'status': 'error', 'message': 'Invalid parameters'}, status=400)
    
    try:
        question = Question.objects.get(pk=question_id, is_active=True)
    except Question.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Question not found'}, status=404)
    
    existing_vote = QuestionLikes.objects.filter(user=request.user, question=question).first()
    
    if existing_vote:
        if existing_vote.reaction == vote_type:
            if vote_type == 'like':
                question.like(-1)
            else:
                question.like(1)
            existing_vote.delete()
            return JsonResponse({
                'status': 'success',
                'rating': question.likes,
                'user_vote': None
            })
        else:
            if vote_type == 'like':
                question.like(2)
            else:
                question.like(-2)
            existing_vote.reaction = vote_type
            existing_vote.save()
            return JsonResponse({
                'status': 'success',
                'rating': question.likes,
                'user_vote': vote_type
            })
    else:
        QuestionLikes.objects.create(
            user=request.user,
            question=question,
            reaction=vote_type
        )
        if vote_type == 'like':
            question.like(1)
        else:
            question.like(-1)
        
        return JsonResponse({
            'status': 'success',
            'rating': question.likes,
            'user_vote': vote_type
        })


@require_POST
@csrf_protect
def vote_answer(request):
    if not request.user.is_authenticated:
        return JsonResponse({'status': 'error', 'message': 'Authentication required'}, status=401)
    
    answer_id = request.POST.get('answer_id')
    vote_type = request.POST.get('vote_type')
    
    if not answer_id or vote_type not in ['like', 'dislike']:
        return JsonResponse({'status': 'error', 'message': 'Invalid parameters'}, status=400)
    
    try:
        answer = Answer.objects.get(pk=answer_id, is_active=True)
    except Answer.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Answer not found'}, status=404)
    
    existing_vote = AnswerLikes.objects.filter(user=request.user, answer=answer).first()
    
    if existing_vote:
        if existing_vote.reaction == vote_type:
            if vote_type == 'like':
                answer.like(-1)
            else:
                answer.like(1)
            existing_vote.delete()
            return JsonResponse({
                'status': 'success',
                'rating': answer.likes,
                'user_vote': None
            })
        else:
            if vote_type == 'like':
                answer.like(2)
            else:
                answer.like(-2)
            existing_vote.reaction = vote_type
            existing_vote.save()
            return JsonResponse({
                'status': 'success',
                'rating': answer.likes,
                'user_vote': vote_type
            })
    else:
        AnswerLikes.objects.create(
            user=request.user,
            answer=answer,
            reaction=vote_type
        )
        if vote_type == 'like':
            answer.like(1)
        else:
            answer.like(-1)
        
        return JsonResponse({
            'status': 'success',
            'rating': answer.likes,
            'user_vote': vote_type
        })


@require_POST
@csrf_protect
def mark_correct_answer(request):
    if not request.user.is_authenticated:
        return JsonResponse({'status': 'error', 'message': 'Authentication required'}, status=401)
    
    answer_id = request.POST.get('answer_id')
    
    if not answer_id:
        return JsonResponse({'status': 'error', 'message': 'Invalid parameters'}, status=400)
    
    try:
        answer = Answer.objects.select_related('question').get(pk=answer_id, is_active=True)
    except Answer.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Answer not found'}, status=404)
    
    if answer.question.author != request.user:
        return JsonResponse({'status': 'error', 'message': 'Only question author can mark correct answer'}, status=403)
    
    answer.is_correct = not answer.is_correct
    answer.save()
    
    return JsonResponse({
        'status': 'success',
        'is_correct': answer.is_correct
    })