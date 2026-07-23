from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register('garages', views.GarageViewSet)
router.register('customers', views.CustomerViewSet)
router.register('vehicles', views.VehicleViewSet)
router.register('work-orders', views.WorkOrderViewSet)
router.register('inventory', views.InventoryViewSet)
router.register('payments', views.PaymentViewSet)
router.register('appointments', views.AppointmentViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('dashboard/', views.dashboard),
]
