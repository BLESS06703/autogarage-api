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
router.register('user-roles', views.UserRoleVS)
router.register('mechanics', views.MechanicProfileVS)
router.register('services', views.ServiceCatalogVS)
router.register('work-order-services', views.WorkOrderServiceVS)

urlpatterns = [
    path('', include(router.urls)),
    path('auth/register/', auth_views.register),
    path('auth/login/', auth_views.login),
    path('auth/login-page/', auth_views.login_page),
    path('auth/register-page/', auth_views.register_page),
    path('dashboard/', dashboard_views.dashboard),
    path('reports/revenue/', report_views.revenue_report),
    path('reports/jobs/', report_views.jobs_report),
]
