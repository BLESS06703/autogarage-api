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
class UserRoleVS(viewsets.ModelViewSet): queryset = UserRole.objects.all(); serializer_class = UserRoleSerializer
class MechanicProfileVS(viewsets.ModelViewSet): queryset = MechanicProfile.objects.all(); serializer_class = MechanicProfileSerializer
class ServiceCatalogVS(viewsets.ModelViewSet): queryset = ServiceCatalog.objects.all(); serializer_class = ServiceCatalogSerializer
class WorkOrderServiceVS(viewsets.ModelViewSet): queryset = WorkOrderService.objects.all(); serializer_class = WorkOrderServiceSerializer
class WorkOrderPartVS(viewsets.ModelViewSet): queryset = WorkOrderPart.objects.all(); serializer_class = WorkOrderPartSerializer
class ServiceHistoryVS(viewsets.ModelViewSet): queryset = ServiceHistory.objects.all(); serializer_class = ServiceHistorySerializer
class DiagnosticRecordVS(viewsets.ModelViewSet): queryset = DiagnosticRecord.objects.all(); serializer_class = DiagnosticRecordSerializer
class InvoiceVS(viewsets.ModelViewSet): queryset = Invoice.objects.all(); serializer_class = InvoiceSerializer
