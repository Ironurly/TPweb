from .models import Tag

class AsideTagsView():
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["tags"] = Tag.objects.all()[:5]
        return context
    