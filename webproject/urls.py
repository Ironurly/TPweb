from django.urls import re_path
from webproject.views import DetailView, index_view

app_name = "webproject"
urlpatterns = [
    re_path(r'^list/', index_view, name="index_question_view"),
    re_path(r'^(?P<pk>\d+)/detail/', DetailView.as_view(), name="question_detail")
]
