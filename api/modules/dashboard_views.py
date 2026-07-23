from rest_framework.decorators import api_view
from rest_framework.response import Response
from api.models import *

@api_view(['GET'])
def dashboard(request):
    return Response({
        'total_customers': Customer.objects.count(),
        'total_vehicles': Vehicle.objects.count(),
        'active_jobs': WorkOrder.objects.filter(status__in=['In Progress','Awaiting Parts']).count(),
        'completed_today': WorkOrder.objects.filter(status='Completed').count(),
        'total_revenue': sum(float(p.amount) for p in Payment.objects.all()),
        'low_stock': InventoryItem.objects.filter(quantity__lt=models.F('min_threshold')).count(),
    })
