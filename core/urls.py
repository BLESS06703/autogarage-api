from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path('', views.home),
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),
] + static('/static/', document_root=settings.STATIC_ROOT) + static('/api/templates/', document_root=settings.BASE_DIR / 'api' / 'templates')
