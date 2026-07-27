from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from .modules import auth_views, dashboard_views, report_views, ai_views, chart_views, intake_views, docs_views, docs_views

router = DefaultRouter()
router.register('garages', views.GarageVS, basename='garage')
router.register('customers', views.CustomerVS, basename='customer')
router.register('vehicles', views.VehicleVS, basename='vehicle')
router.register('work-orders', views.WorkOrderVS, basename='workorder')
router.register('inventory', views.InventoryVS, basename='inventory')
router.register('payments', views.PaymentVS, basename='payment')
router.register('appointments', views.AppointmentVS, basename='appointment')
router.register('user-roles', views.UserRoleVS, basename='userrole')
router.register('mechanics', views.MechanicProfileVS, basename='mechanic')
router.register('services', views.ServiceCatalogVS, basename='service')
router.register('work-order-services', views.WorkOrderServiceVS, basename='workorderservice')
router.register('work-order-parts', views.WorkOrderPartVS, basename='workorderpart')
router.register('service-history', views.ServiceHistoryVS, basename='servicehistory')
router.register('diagnostics', views.DiagnosticRecordVS, basename='diagnostic')
router.register('invoices', views.InvoiceVS, basename='invoice')
router.register('notifications', views.NotificationVS, basename='notification')

urlpatterns = [
    path('', include(router.urls)),
    path('auth/register/', auth_views.register),
    path('auth/login/', auth_views.login),
    path('auth/login-page/', auth_views.login_page),
    path('auth/register-page/', auth_views.register_page),
    path('dashboard/', dashboard_views.dashboard),
    path('dashboard-page/', dashboard_views.dashboard_page),
    path('offline/', dashboard_views.offline_page),
    path('reports/revenue/', report_views.revenue_report),
    path('reports/jobs/', report_views.jobs_report),
    path('ai/diagnose/', ai_views.ai_diagnose),
    path('ai/codes/', ai_views.ai_codes_list),
    path('charts/revenue/', chart_views.revenue_chart),
    path('charts/status/', chart_views.status_chart),
    path('charts/repairs/', chart_views.repairs_chart),
    path('charts/mechanics/', chart_views.mechanics_chart),
    path('charts/all/', chart_views.all_charts),
    path('intake/', intake_views.quick_intake),
    path('docs/', docs_views.api_docs),
    path('quick-customer/', intake_views.quick_customer),
    path('quick-vehicle/', intake_views.quick_vehicle),
    path('quick-workorder/', intake_views.quick_workorder),
]
