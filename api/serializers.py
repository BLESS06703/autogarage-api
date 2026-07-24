from rest_framework import serializers
from .models import *

class GarageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Garage
        fields = '__all__'

class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = '__all__'
        read_only_fields = ['garage', 'reference_number']

class VehicleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vehicle
        fields = '__all__'
        read_only_fields = ['garage']

class WorkOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkOrder
        fields = '__all__'
        read_only_fields = ['garage', 'srn']

class InventorySerializer(serializers.ModelSerializer):
    class Meta:
        model = InventoryItem
        fields = '__all__'
        read_only_fields = ['garage']

class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = '__all__'

class AppointmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Appointment
        fields = '__all__'
        read_only_fields = ['garage']

class UserRoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserRole
        fields = '__all__'

class MechanicProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = MechanicProfile
        fields = ['id', 'user', 'username', 'full_name', 'garage', 'skills', 'is_available', 'phone', 'hire_date', 'created_at']
        read_only_fields = ['garage']

    def get_full_name(self, obj):
        return obj.user.get_full_name() or obj.user.username

class ServiceCatalogSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceCatalog
        fields = '__all__'
        read_only_fields = ['garage']

class WorkOrderServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkOrderService
        fields = '__all__'

class WorkOrderPartSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkOrderPart
        fields = '__all__'

class ServiceHistorySerializer(serializers.ModelSerializer):
    vehicle_plate = serializers.CharField(source='vehicle.plate', read_only=True)
    mechanic_name = serializers.SerializerMethodField()

    class Meta:
        model = ServiceHistory
        fields = '__all__'
        read_only_fields = ['garage']

    def get_mechanic_name(self, obj):
        return obj.mechanic.user.get_full_name() if obj.mechanic else None

class DiagnosticRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = DiagnosticRecord
        fields = '__all__'

class InvoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Invoice
        fields = '__all__'
        read_only_fields = ['garage', 'invoice_number']
