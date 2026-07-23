from rest_framework import viewsets
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import *
from .serializers import *

class GarageViewSet(viewsets.ModelViewSet):
    queryset = Garage.objects.all()
    serializer_class = GarageSerializer

class CustomerViewSet(viewsets.ModelViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer

class VehicleViewSet(viewsets.ModelViewSet):
    queryset = Vehicle.objects.all()
    serializer_class = VehicleSerializer

class WorkOrderViewSet(viewsets.ModelViewSet):
    queryset = WorkOrder.objects.all()
    serializer_class = WorkOrderSerializer

class InventoryViewSet(viewsets.ModelViewSet):
    queryset = InventoryItem.objects.all()
    serializer_class = InventorySerializer

class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer

class AppointmentViewSet(viewsets.ModelViewSet):
    queryset = Appointment.objects.all()
    serializer_class = AppointmentSerializer

@api_view(['GET'])
def dashboard(request):
    return Response({
        'total_garages': Garage.objects.count(),
        'total_customers': Customer.objects.count(),
        'active_jobs': WorkOrder.objects.filter(status__in=['In Progress','Awaiting Parts']).count(),
        'total_revenue': sum(p.amount for p in Payment.objects.all()),
    })
