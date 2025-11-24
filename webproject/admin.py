from django.contrib import admin

from webproject.models import Answer, AnswerLikes, Question, QuestionLikes, Tag, UserProfile

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    ...

@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    ...

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    ...

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    ...

@admin.register(QuestionLikes)
class QuestionLikesAdmin(admin.ModelAdmin):
    ...

@admin.register(AnswerLikes)
class AnswerLikesAdmin(admin.ModelAdmin):
    ...