from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),
]

from django.http import HttpResponse
def home(request):
    return HttpResponse("<h1>AutoGarage API</h1><p>API is running. Visit <a href='/api/'>/api/</a></p>")
urlpatterns.insert(0, path('', home))
