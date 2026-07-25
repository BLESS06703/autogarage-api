from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve
from . import views

urlpatterns = [
    path('', views.home),
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),
    # Serve template files (CSS, JS, images)
    path('static/dashboard.css', serve, {'document_root': settings.BASE_DIR / 'api' / 'templates', 'path': 'dashboard.css'}),
    path('static/dashboard.js', serve, {'document_root': settings.BASE_DIR / 'api' / 'templates', 'path': 'dashboard.js'}),
    path('static/logo.png', serve, {'document_root': settings.BASE_DIR / 'api' / 'templates', 'path': 'logo.png'}),
]
