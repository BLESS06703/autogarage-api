from rest_framework import viewsets
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import *
from .serializers import *

class GarageVS(viewsets.ModelViewSet): queryset = Garage.objects.all(); serializer_class = GarageSerializer
class CustomerVS(viewsets.ModelViewSet): queryset = Customer.objects.all(); serializer_class = CustomerSerializer
class WorkOrderVS(viewsets.ModelViewSet): queryset = WorkOrder.objects.all(); serializer_class = WorkOrderSerializer
class InventoryVS(viewsets.ModelViewSet): queryset = InventoryItem.objects.all(); serializer_class = InventorySerializer
class PaymentVS(viewsets.ModelViewSet): queryset = Payment.objects.all(); serializer_class = PaymentSerializer

@api_view(['GET'])
def dashboard(r):
    return Response({'customers':Customer.objects.count(),'active':WorkOrder.objects.filter(status='In Progress').count(),'revenue':sum(float(p.amount) for p in Payment.objects.all())})
