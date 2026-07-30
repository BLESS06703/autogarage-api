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
    vehicle_info = serializers.SerializerMethodField()
    customer_name = serializers.SerializerMethodField()

    class Meta:
        model = WorkOrder
        fields = [
            'id',
            'status',
            'issue_description',
            'cost_estimate',
            'srn',
            'created_at',
            'completed_at',
            'vehicle',
            'garage',
            'mechanic',
            'vehicle_info',
            'customer_name',
        ]
        read_only_fields = ['garage', 'srn']

    def get_vehicle_info(self, obj):
        if obj.vehicle:
            return f"{obj.vehicle.make} {obj.vehicle.model_name} - {obj.vehicle.plate}"
        return None

    def get_customer_name(self, obj):
        if obj.vehicle and obj.vehicle.customer:
            return obj.vehicle.customer.full_name
        return None

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

class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = '__all__'
        read_only_fields = ['garage', 'created_at']

class AuditLogSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    class Meta:
        model = AuditLog
        fields = '__all__'

class CartItemSerializer(serializers.ModelSerializer):
    part_name = serializers.CharField(source='inventory_item.part_name', read_only=True)
    class Meta:
        model = CartItem
        fields = ['id', 'inventory_item', 'part_name', 'quantity', 'unit_price', 'total_price']

class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    customer_name = serializers.CharField(source='customer.full_name', read_only=True)
    class Meta:
        model = Cart
        fields = ['id', 'customer', 'customer_name', 'garage', 'items', 'is_checked_out', 'created_at']

class OrderSerializer(serializers.ModelSerializer):
    customer_name = serializers.CharField(source='customer.full_name', read_only=True)
    items = CartItemSerializer(source='cart.items', many=True, read_only=True)
    class Meta:
        model = Order
        fields = '__all__'
