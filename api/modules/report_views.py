from rest_framework.decorators import api_view
from rest_framework.response import Response
from api.models import *
from django.db.models import Sum, Count

@api_view(['GET'])
def revenue_report(request):
    total = Payment.objects.aggregate(total=Sum('amount'))
    return Response({'total_revenue': total['total'] or 0})

@api_view(['GET'])
def jobs_report(request):
    return Response({'total': WorkOrder.objects.count(), 'by_status': {s[0]: WorkOrder.objects.filter(status=s[0]).count() for s in WorkOrder.STATUS}})
