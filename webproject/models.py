from django.db import models
from django.contrib.auth.models import User
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

#functions
class QuestionManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_active=True)
    
    def all_objects(self):
        return super().get_queryset()

    def get_hot_questions(self):
        return self.filter(is_active=True) \
            .select_related('author') \
            .prefetch_related('tags') \
            .order_by('-likes')

    def get_new_questions(self):
        return self.filter(is_active=True) \
            .select_related('author') \
            .prefetch_related('tags') \
            .order_by('-created_at')
    
    def get_tagged_questions(self, tag_id):
        return self.filter(
                tags__id=tag_id,
                is_active=True
            ).select_related('author') \
            .prefetch_related('tags') \
            .order_by("-created_at")
    
    def get_question_by_id(self, id):
        return self.filter(is_active=True) \
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
    
#models for db
class Tag(models.Model):
    title = models.CharField(verbose_name="Имя тега", max_length=255, unique=True)
    
    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.title

class UserProfile(models.Model):
    avatar = models.CharField(verbose_name="Аватар пользователя", max_length=255, blank=True, null=True)
    bio = models.TextField(verbose_name="Описание", max_length=4000)
    
    user = models.OneToOneField(User, verbose_name="Пользователь", on_delete=models.CASCADE)
    class Meta:
        verbose_name = 'Профиль пользователя'
        verbose_name_plural = 'Профиль пользователей'
        
    def __str__(self):
        return f"#{self.id}: Профиль пользователя {self.user_id}"

class Question(models.Model):
    title = models.CharField(verbose_name="Заголовок", max_length=255)
    body = models.TextField(verbose_name="Текст вопроса", max_length="4000")
    
    likes = models.IntegerField(default=0, db_index=True)
    answers_count = models.IntegerField(default=0)
    tags = models.ManyToManyField(Tag, blank = True, db_index=True)
    
    author = models.ForeignKey(User, verbose_name="Автор вопроса", on_delete=models.SET_NULL, null=True)
    
    created_at = models.DateTimeField(verbose_name="Время создания", auto_now_add=True, db_index=True)
    
    is_active = models.BooleanField(verbose_name="Активно", help_text="Если True - отображается", default=True, db_index=True)

    objects = QuestionManager()
    
    def answer(self):
        self.answers_count += 1
        self.save(update_fields=["answers_count"])

    def like(self, val):
        self.likes += val
        self.save(update_fields=["likes"])

    class Meta:
        verbose_name = 'Вопрос'
        verbose_name_plural = 'Вопросы'
        
    def __str__(self):
        return f"#{self.id}: {self.title}"

class Answer(models.Model):
    body = models.TextField(verbose_name="Текст комментария", max_length="4000")
    
    likes = models.IntegerField(default=0)
    is_correct = models.BooleanField(verbose_name="Верный", default=False)
    
    author = models.ForeignKey(User, verbose_name="Автор комментария", on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(verbose_name="Время создания", auto_now_add=True)
    
    question = models.ForeignKey(Question, verbose_name="Вопрос", on_delete=models.CASCADE, related_name="answers")
    is_active = models.BooleanField(verbose_name="Активно", help_text="Если True - отображается", default=True, db_index=True)

    def like(self, val):
        self.likes += val
        self.save(update_fields=["likes"])
    
    class Meta:
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'
        
    def __str__(self):
        return f"#{self.id}: {self.title}"


class QuestionLikes(models.Model):
    
    LIKE = 'like'
    DISLIKE = 'dislike'
    
    REACTION_CHOICES = [
        (LIKE, 'Лайк'),
        (DISLIKE, 'Дизлайк')
    ]

    reaction = models.CharField(
        max_length=15,
        choices=REACTION_CHOICES
    )

    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Лайк Вопроса'
        verbose_name_plural = 'Лайки Вопросов'
        unique_together = ['user', 'question']
    
    def __str__(self):
        return f"#{self.id}: лайк от {self.user_id} к посту {self.question_id}"


class AnswerLikes(models.Model):
    
    LIKE = 'like'
    DISLIKE = 'dislike'
    
    REACTION_CHOICES = [
        (LIKE, 'Лайк'),
        (DISLIKE, 'Дизлайк')
    ]

    reaction = models.CharField(
        max_length=15,
        choices=REACTION_CHOICES
    )
    
    answer = models.ForeignKey(Answer, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    
    class Meta:
        verbose_name = 'Лайк Комментария'
        verbose_name_plural = 'Лайки Комментариев'
        unique_together = ['user', 'answer']
        
    def __str__(self):
        return f"#{self.id}: лайк от {self.user_id} к комментарию {self.answer_id}"