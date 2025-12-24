from django.urls import re_path
from webproject.views import *

app_name = "webproject"
urlpatterns = [
    re_path(r'^$', IndexQuestionView.as_view(), name="index_question_view"),
    re_path(r'^hot/$', HotQuestionView.as_view(), name="hot_question_view"),
    re_path(r'^detail/(?P<pk>\d+)/$', QuestionDetailView.as_view(), name="question_detail"),
    re_path(r'^ask/$', AskView.as_view(), name="ask_question"),
    re_path(r'^tag/(?P<tag_name>[\w-]+)/$', TagView.as_view(), name="tag"),
    
    re_path(r'^ajax/vote-question/$', vote_question, name="vote_question"),
    re_path(r'^ajax/vote-answer/$', vote_answer, name="vote_answer"),
    re_path(r'^ajax/mark-correct/$', mark_correct_answer, name="mark_correct_answer"),
]
