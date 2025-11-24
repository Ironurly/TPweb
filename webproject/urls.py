from django.urls import re_path
from webproject.views import *

app_name = "webproject"
urlpatterns = [
    re_path(r'^$', IndexQuestionView.as_view(), name="index_question_view"),
    re_path(r'^hot/$', HotQuestionView.as_view(), name="hot_question_view"),
    re_path(r'^detail/(?P<pk>\d+)/$', QuestionDetailView.as_view(), name="question_detail"),
    re_path(r'^ask/$', AskView.as_view(), name="ask_question"),
    re_path(r'^tag/(?P<tag_name>[\w-]+)/$', TagView.as_view(), name="tag"),
]
