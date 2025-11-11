from django.contrib import admin
from django.urls import include, re_path
from django.conf import settings
from django.conf.urls.static import static
urlpatterns = [
    re_path(r'^admin/', admin.site.urls),
    re_path(r'^', include('webproject.urls')),
]
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)