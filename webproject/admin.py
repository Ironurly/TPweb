from django.contrib import admin

from webproject.models import Comment, CommentLikes, Question, QuestionLikes, Tag, UserProfile

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    ...

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
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

@admin.register(CommentLikes)
class CommentLikesAdmin(admin.ModelAdmin):
    ...