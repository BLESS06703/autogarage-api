from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
r = DefaultRouter()
r.register('garages', views.GarageVS)
r.register('customers', views.CustomerVS)
r.register('work-orders', views.WorkOrderVS)
r.register('inventory', views.InventoryVS)
r.register('payments', views.PaymentVS)
urlpatterns = [path('', include(r.urls)), path('dashboard/', views.dashboard)]
