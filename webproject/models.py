from django.db import models
from django.contrib.auth.models import User

class Tag(models.Model):
    title = models.CharField(verbose_name="Имя тега", max_length=255)
    
    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'
        
    def __str__(self):
        return self.title

class UserProfile(models.Model):
    avatar = models.CharField(verbose_name="Аватар пользователя", max_length=255, blank=True, null=True)
    bio = models.TextField(verbose_name="Описание", max_length=4000)
    
    user = models.ForeignKey(User, verbose_name="Пользователь", on_delete=models.CASCADE)
    class Meta:
        verbose_name = 'Профиль пользователя'
        verbose_name_plural = 'Профиль пользователей'
        
    def __str__(self):
        return f"#{self.id}: Профиль пользователя {self.user.username}"

class Question(models.Model):
    title = models.CharField(verbose_name="Заголовок", max_length=255)
    body = models.TextField(verbose_name="Текст вопроса", max_length="4000")
    
    likes = models.IntegerField(default=0)
    answers = models.IntegerField(default=0)
    tags = models.ManyToManyField(Tag, blank = True)
    
    author_id = models.ForeignKey(User, verbose_name="Автор вопроса", on_delete=models.SET_NULL, null=True)
    
    created_at =models.DateTimeField(verbose_name="Время создания", auto_now_add=True)
    
    is_active = models.BooleanField(verbose_name="Активно", help_text="Если True - отображается", default=True)

    def answer(self):
        self.answers += 1
        self.save()

    def like(self, val):
        self.likes += val
        self.save()

    class Meta:
        verbose_name = 'Вопрос'
        verbose_name_plural = 'Вопросы'
        
    def __str__(self):
        return f"#{self.id}: {self.title}"

class Comment(models.Model):
    title = models.CharField(verbose_name="Заголовок", max_length=255)
    body = models.TextField(verbose_name="Текст комментария", max_length="4000")
    
    likes = models.IntegerField(default=0)
    is_correct = models.BooleanField(verbose_name="Верный", default=False)
    
    author_id = models.ForeignKey(User, verbose_name="Автор комментария", on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(verbose_name="Время создания", auto_now_add=True)
    
    question_id = models.ForeignKey(Question, verbose_name="Вопрос", on_delete=models.CASCADE, related_name="comments")
    is_active = models.BooleanField(verbose_name="Активно", help_text="Если True - отображается", default=True)
    
    def save(self, *args, **kwargs):
        self.question_id.answer()
        super().save(*args, **kwargs)

    def like(self, val):
        self.likes += val
        self.save()
    
    class Meta:
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'
        
    def __str__(self):
        return f"#{self.id}: {self.title}"


class QuestionLikes(models.Model):
    status = models.BooleanField(null=True)

    question_id = models.ForeignKey(Question, on_delete=models.CASCADE)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    
    def save(self, *args, **kwargs):
        
        if self.status == True:
            self.question_id.like(1)
        elif self.status == False:
            self.question_id.like(-1)
        
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Лайк Вопроса'
        verbose_name_plural = 'Лайки Вопросов'
        unique_together = ['user_id', 'question_id']
    
    def __str__(self):
        return f"#{self.id}: лайк от {self.user_id.username} к посту {self.question_id.id} {self.question_id.title}"


class CommentLikes(models.Model):
    status = models.BooleanField(null=True)

    comment_id = models.ForeignKey(Comment, on_delete=models.CASCADE)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    
    def save(self, *args, **kwargs):
        
        if self.status == True:
            self.comment_id.like(1)
        elif self.status == False:
            self.comment_id.like(-1)
        
        super().save(*args, **kwargs)
    
    class Meta:
        verbose_name = 'Лайк Комментария'
        verbose_name_plural = 'Лайки Комментариев'
        unique_together = ['user_id', 'comment_id']
        
    def __str__(self):
        return f"#{self.id}: лайк от {self.user_id.username} к комментарию {self.comment_id.id} {self.comment_id.title}"