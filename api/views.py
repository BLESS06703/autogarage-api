from rest_framework import viewsets
from .models import *
from .serializers import *

class GarageVS(viewsets.ModelViewSet): queryset = Garage.objects.all(); serializer_class = GarageSerializer
class CustomerVS(viewsets.ModelViewSet): queryset = Customer.objects.all(); serializer_class = CustomerSerializer
class VehicleVS(viewsets.ModelViewSet): queryset = Vehicle.objects.all(); serializer_class = VehicleSerializer
class WorkOrderVS(viewsets.ModelViewSet): queryset = WorkOrder.objects.all(); serializer_class = WorkOrderSerializer
class InventoryVS(viewsets.ModelViewSet): queryset = InventoryItem.objects.all(); serializer_class = InventorySerializer
class PaymentVS(viewsets.ModelViewSet): queryset = Payment.objects.all(); serializer_class = PaymentSerializer
class AppointmentVS(viewsets.ModelViewSet): queryset = Appointment.objects.all(); serializer_class = AppointmentSerializer
