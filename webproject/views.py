from django.shortcuts import render
from django.views import View
from django.views.generic import TemplateView
from rest_framework.generics import RetrieveAPIView
from django.core.paginator import Paginator
# Create your views here.
def index_view(request):
    questions = []
    for i in range(50):
        questions.append({
            "id": i,
            "text": f"LONG_TEXT {i}",
            "description": "Guys, i have trouble with a moon park. Can't find the black-jack..."
        })
    
    page_number = request.GET.get("page", 1)
    page = Paginator(questions, per_page=5) 

    object_list = page.page(page_number)


    return render(request, "index.html", context={"object_list": object_list, "page_obj": page})

class DetailView(TemplateView):
    template_name = "index.html"

    def get_context_data(self, **kwargs):
        return super().get_context_data(**kwargs)