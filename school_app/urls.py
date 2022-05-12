from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include, re_path
from django.views.generic import TemplateView

urlpatterns = [
                  path('admin/', admin.site.urls),
                  path('api/', include('api.urls', namespace='api')),
              ] + static(settings.FILE_URL, document_root=settings.FILE_ROOT) \
                + [re_path(r'^.*', TemplateView.as_view(template_name='index.html'))]
