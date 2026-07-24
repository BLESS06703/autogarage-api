from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from api.models import *
from api.views import get_user_garage

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard(request):
    user = request.user
    garage = get_user_garage(user)
    
    if not garage and not user.is_superuser:
        return Response({'error': 'No garage assigned'}, status=403)
    
    customers = Customer.objects.filter(garage=garage) if garage else Customer.objects.all()
    vehicles = Vehicle.objects.filter(garage=garage) if garage else Vehicle.objects.all()
    work_orders = WorkOrder.objects.filter(garage=garage) if garage else WorkOrder.objects.all()
    payments = Payment.objects.filter(work_order__garage=garage) if garage else Payment.objects.all()
    inventory = InventoryItem.objects.filter(garage=garage) if garage else InventoryItem.objects.all()
    
    return Response({
        'total_customers': customers.count(),
        'total_vehicles': vehicles.count(),
        'active_jobs': work_orders.filter(status__in=['In Progress', 'Awaiting Parts']).count(),
        'completed_today': work_orders.filter(status='Completed').count(),
        'total_revenue': sum(float(p.amount) for p in payments),
        'low_stock': inventory.filter(quantity__lt=models.F('min_threshold')).count(),
    })

from django.shortcuts import render

def dashboard_page(request):
    return render(request, 'dashboard.html')

def offline_page(request):
    return render(request, 'offline.html')
