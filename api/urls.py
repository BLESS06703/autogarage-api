from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from .modules import auth_views, dashboard_views, report_views

router = DefaultRouter()
router.register('garages', views.GarageVS)
router.register('customers', views.CustomerVS)
router.register('vehicles', views.VehicleVS)
router.register('work-orders', views.WorkOrderVS)
router.register('inventory', views.InventoryVS)
router.register('payments', views.PaymentVS)
router.register('appointments', views.AppointmentVS)

urlpatterns = [
    path('', include(router.urls)),
    path('auth/register/', auth_views.register),
    path('auth/login/', auth_views.login),
    path('dashboard/', dashboard_views.dashboard),
    path('reports/revenue/', report_views.revenue_report),
    path('reports/jobs/', report_views.jobs_report),
]

# JWT endpoints
from rest_framework_simplejwt.views import TokenRefreshView
urlpatterns += [
    path('auth/refresh/', TokenRefreshView.as_view()),
    path('auth/profile/', auth_views.profile),
]
