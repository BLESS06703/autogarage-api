from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponse

def home(r): return HttpResponse('<h1>AutoGarage API</h1><a href="/api/">API</a>')

urlpatterns = [path('', home), path('admin/', admin.site.urls), path('api/', include('api.urls'))]
