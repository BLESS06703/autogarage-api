from rest_framework import viewsets, permissions
from rest_framework.exceptions import PermissionDenied
from .models import *
from .serializers import *

# ==================== BASE PERMISSION ====================
class IsGarageMember(permissions.BasePermission):
    """Only allow access to data belonging to user's garage"""
    def has_permission(self, request, view):
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        # Superusers can access everything
        if request.user.is_superuser:
            return True
        # Check if object has garage field and matches user's garage
        garage = getattr(obj, 'garage', None)
        if garage:
            user_garage = self._get_user_garage(request.user)
            return garage == user_garage
        return False

    def _get_user_garage(self, user):
        try:
            role = UserRole.objects.get(user=user)
            return role.garage
        except UserRole.DoesNotExist:
            return None


class GarageOwnerPermission(permissions.BasePermission):
    """Only garage owners/admins can modify garage data"""
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        if request.user.is_superuser:
            return True
        try:
            role = UserRole.objects.get(user=request.user)
            return role.role in ['admin', 'owner', 'manager']
        except UserRole.DoesNotExist:
            return False


def get_user_garage(user):
    """Helper to get a user's assigned garage"""
    try:
        role = UserRole.objects.get(user=user)
        return role.garage
    except UserRole.DoesNotExist:
        return None


# ==================== GARAGES ====================
class GarageVS(viewsets.ModelViewSet):
    serializer_class = GarageSerializer
    permission_classes = [IsGarageMember]

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return Garage.objects.all()
        garage = get_user_garage(user)
        if garage:
            return Garage.objects.filter(id=garage.id)
        return Garage.objects.none()

    def perform_create(self, serializer):
        garage = serializer.save()
        # Auto-assign creator as owner
        UserRole.objects.get_or_create(
            user=self.request.user,
            defaults={'role': 'owner', 'garage': garage}
        )


# ==================== CUSTOMERS ====================
class CustomerVS(viewsets.ModelViewSet):
    serializer_class = CustomerSerializer
    permission_classes = [IsGarageMember, GarageOwnerPermission]

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return Customer.objects.all()
        garage = get_user_garage(user)
        if garage:
            return Customer.objects.filter(garage=garage)
        return Customer.objects.none()

    def perform_create(self, serializer):
        garage = get_user_garage(self.request.user)
        if not garage:
            raise PermissionDenied("No garage assigned to your account")
        serializer.save(garage=garage)


# ==================== VEHICLES ====================
class VehicleVS(viewsets.ModelViewSet):
    serializer_class = VehicleSerializer
    permission_classes = [IsGarageMember, GarageOwnerPermission]

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return Vehicle.objects.all()
        garage = get_user_garage(user)
        if garage:
            return Vehicle.objects.filter(garage=garage)
        return Vehicle.objects.none()

    def perform_create(self, serializer):
        garage = get_user_garage(self.request.user)
        if not garage:
            raise PermissionDenied("No garage assigned to your account")
        serializer.save(garage=garage)


# ==================== WORK ORDERS ====================
class WorkOrderVS(viewsets.ModelViewSet):
    serializer_class = WorkOrderSerializer
    permission_classes = [IsGarageMember]

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return WorkOrder.objects.all()
        garage = get_user_garage(user)
        if garage:
            return WorkOrder.objects.filter(garage=garage)
        return WorkOrder.objects.none()

    def perform_create(self, serializer):
        garage = get_user_garage(self.request.user)
        if not garage:
            raise PermissionDenied("No garage assigned to your account")
        serializer.save(garage=garage)


# ==================== INVENTORY ====================
class InventoryVS(viewsets.ModelViewSet):
    serializer_class = InventorySerializer
    permission_classes = [IsGarageMember, GarageOwnerPermission]

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return InventoryItem.objects.all()
        garage = get_user_garage(user)
        if garage:
            return InventoryItem.objects.filter(garage=garage)
        return InventoryItem.objects.none()

    def perform_create(self, serializer):
        garage = get_user_garage(self.request.user)
        if not garage:
            raise PermissionDenied("No garage assigned to your account")
        serializer.save(garage=garage)


# ==================== PAYMENTS ====================
class PaymentVS(viewsets.ModelViewSet):
    serializer_class = PaymentSerializer
    permission_classes = [IsGarageMember]

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return Payment.objects.all()
        garage = get_user_garage(user)
        if garage:
            return Payment.objects.filter(work_order__garage=garage)
        return Payment.objects.none()


# ==================== APPOINTMENTS ====================
class AppointmentVS(viewsets.ModelViewSet):
    serializer_class = AppointmentSerializer
    permission_classes = [IsGarageMember]

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return Appointment.objects.all()
        garage = get_user_garage(user)
        if garage:
            return Appointment.objects.filter(garage=garage)
        return Appointment.objects.none()

    def perform_create(self, serializer):
        garage = get_user_garage(self.request.user)
        if not garage:
            raise PermissionDenied("No garage assigned to your account")
        serializer.save(garage=garage)


# ==================== USER ROLES ====================
class UserRoleVS(viewsets.ModelViewSet):
    serializer_class = UserRoleSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return UserRole.objects.all()
        garage = get_user_garage(user)
        if garage:
            return UserRole.objects.filter(garage=garage)
        return UserRole.objects.filter(user=user)


# ==================== MECHANIC PROFILES ====================
class MechanicProfileVS(viewsets.ModelViewSet):
    serializer_class = MechanicProfileSerializer
    permission_classes = [IsGarageMember]

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return MechanicProfile.objects.all()
        garage = get_user_garage(user)
        if garage:
            return MechanicProfile.objects.filter(garage=garage)
        return MechanicProfile.objects.none()

    def perform_create(self, serializer):
        garage = get_user_garage(self.request.user)
        if not garage:
            raise PermissionDenied("No garage assigned to your account")
        serializer.save(garage=garage)


# ==================== SERVICE CATALOG ====================
class ServiceCatalogVS(viewsets.ModelViewSet):
    serializer_class = ServiceCatalogSerializer
    permission_classes = [IsGarageMember]

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return ServiceCatalog.objects.all()
        garage = get_user_garage(user)
        if garage:
            return ServiceCatalog.objects.filter(garage=garage)
        return ServiceCatalog.objects.none()

    def perform_create(self, serializer):
        garage = get_user_garage(self.request.user)
        if not garage:
            raise PermissionDenied("No garage assigned to your account")
        serializer.save(garage=garage)


# ==================== WORK ORDER SERVICES ====================
class WorkOrderServiceVS(viewsets.ModelViewSet):
    serializer_class = WorkOrderServiceSerializer
    permission_classes = [IsGarageMember]

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return WorkOrderService.objects.all()
        garage = get_user_garage(user)
        if garage:
            return WorkOrderService.objects.filter(work_order__garage=garage)
        return WorkOrderService.objects.none()


# ==================== WORK ORDER PARTS ====================
class WorkOrderPartVS(viewsets.ModelViewSet):
    serializer_class = WorkOrderPartSerializer
    permission_classes = [IsGarageMember]

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return WorkOrderPart.objects.all()
        garage = get_user_garage(user)
        if garage:
            return WorkOrderPart.objects.filter(work_order__garage=garage)
        return WorkOrderPart.objects.none()


# ==================== SERVICE HISTORY ====================
class ServiceHistoryVS(viewsets.ModelViewSet):
    serializer_class = ServiceHistorySerializer
    permission_classes = [IsGarageMember]

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return ServiceHistory.objects.all()
        garage = get_user_garage(user)
        if garage:
            return ServiceHistory.objects.filter(garage=garage)
        return ServiceHistory.objects.none()

    def perform_create(self, serializer):
        garage = get_user_garage(self.request.user)
        if not garage:
            raise PermissionDenied("No garage assigned to your account")
        serializer.save(garage=garage)


# ==================== DIAGNOSTIC RECORDS ====================
class DiagnosticRecordVS(viewsets.ModelViewSet):
    serializer_class = DiagnosticRecordSerializer
    permission_classes = [IsGarageMember]

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return DiagnosticRecord.objects.all()
        garage = get_user_garage(user)
        if garage:
            return DiagnosticRecord.objects.filter(work_order__garage=garage)
        return DiagnosticRecord.objects.none()


# ==================== INVOICES ====================
class InvoiceVS(viewsets.ModelViewSet):
    serializer_class = InvoiceSerializer
    permission_classes = [IsGarageMember]

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return Invoice.objects.all()
        garage = get_user_garage(user)
        if garage:
            return Invoice.objects.filter(garage=garage)
        return Invoice.objects.none()

    def perform_create(self, serializer):
        garage = get_user_garage(self.request.user)
        if not garage:
            raise PermissionDenied("No garage assigned to your account")
        serializer.save(garage=garage)
