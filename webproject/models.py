from django.db import models
from django.contrib.auth.models import User

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
        return f"#{self.id}: Профиль пользователя {self.user}"

class Question(models.Model):
    title = models.CharField(verbose_name="Заголовок", max_length=255)
    body = models.TextField(verbose_name="Текст вопроса", max_length="4000")
    
    likes = models.IntegerField(default=0, db_index=True)
    answers_count = models.IntegerField(default=0)
    tags = models.ManyToManyField(Tag, blank = True, db_index=True)
    
    author = models.ForeignKey(User, verbose_name="Автор вопроса", on_delete=models.SET_NULL, null=True)
    
    created_at = models.DateTimeField(verbose_name="Время создания", auto_now_add=True, db_index=True)
    
    is_active = models.BooleanField(verbose_name="Активно", help_text="Если True - отображается", default=True, db_index=True)

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
    title = models.CharField(verbose_name="Заголовок", max_length=255)
    body = models.TextField(verbose_name="Текст комментария", max_length="4000")
    
    likes = models.IntegerField(default=0)
    is_correct = models.BooleanField(verbose_name="Верный", default=False)
    
    author = models.ForeignKey(User, verbose_name="Автор комментария", on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(verbose_name="Время создания", auto_now_add=True)
    
    question = models.ForeignKey(Question, verbose_name="Вопрос", on_delete=models.CASCADE, related_name="answers")
    is_active = models.BooleanField(verbose_name="Активно", help_text="Если True - отображается", default=True, db_index=True)
    
    
    # Потом когда реализовавывать буду... от туда их вызывать буду
    # def save(self, *args, **kwargs):
    #     self.question.answer()
    #     super().save(*args, **kwargs)

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
    NO_REACTION = 'no_reaction'
    
    REACTION_CHOICES = [
        (LIKE, 'Лайк'),
        (DISLIKE, 'Дизлайк'),
        (NO_REACTION, 'Нет реакции'),
    ]

    reaction = models.CharField(
        max_length=15,
        choices=REACTION_CHOICES,
        default=NO_REACTION
    )

    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Лайк Вопроса'
        verbose_name_plural = 'Лайки Вопросов'
        unique_together = ['user', 'question']
    
    def __str__(self):
        return f"#{self.id}: лайк от {self.user_id} к посту {self.question}"


class AnswerLikes(models.Model):
    
    LIKE = 'like'
    DISLIKE = 'dislike'
    NO_REACTION = 'no_reaction'
    
    REACTION_CHOICES = [
        (LIKE, 'Лайк'),
        (DISLIKE, 'Дизлайк'),
        (NO_REACTION, 'Нет реакции'),
    ]

    reaction = models.CharField(
        max_length=15,
        choices=REACTION_CHOICES,
        default=NO_REACTION
    )
   
    answer = models.ForeignKey(Answer, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    
    class Meta:
        verbose_name = 'Лайк Комментария'
        verbose_name_plural = 'Лайки Комментариев'
        unique_together = ['user', 'answer']
        
    def __str__(self):
        return f"#{self.id}: лайк от {self.user_id} к комментарию {self.answer}"