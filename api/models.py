from django.db import models
from django.contrib.auth.models import User
import random, string

def generate_ref():
    return f"BG-{''.join(random.choices(string.digits, k=5))}"

class Garage(models.Model):
    name = models.CharField(max_length=200)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='garages')
    phone = models.CharField(max_length=20)
    address = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self): return self.name

class Customer(models.Model):
    garage = models.ForeignKey(Garage, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=200)
    phone = models.CharField(max_length=20)
    email = models.EmailField(blank=True)
    reference_number = models.CharField(max_length=20, unique=True, default=generate_ref)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self): return f"{self.full_name} ({self.garage.name})"

class Vehicle(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='vehicles')
    garage = models.ForeignKey(Garage, on_delete=models.CASCADE)
    make = models.CharField(max_length=100)
    model_name = models.CharField(max_length=100)
    year = models.CharField(max_length=10)
    vin = models.CharField(max_length=50, blank=True)
    plate = models.CharField(max_length=20)
    mileage = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self): return f"{self.plate} - {self.make} {self.model_name}"

class WorkOrder(models.Model):
    STATUS = [('In Progress','In Progress'),('Awaiting Parts','Awaiting Parts'),('Ready (Pending Invoice)','Ready (Pending Invoice)'),('Completed','Completed')]
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name='work_orders')
    garage = models.ForeignKey(Garage, on_delete=models.CASCADE)
    mechanic = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    status = models.CharField(max_length=30, choices=STATUS, default='In Progress')
    issue_description = models.TextField(blank=True)
    cost_estimate = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    srn = models.CharField(max_length=20, unique=True, default=generate_ref)
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

class InventoryItem(models.Model):
    garage = models.ForeignKey(Garage, on_delete=models.CASCADE)
    part_name = models.CharField(max_length=200)
    quantity = models.IntegerField(default=0)
    min_threshold = models.IntegerField(default=5)
    unit_price = models.DecimalField(max_digits=12, decimal_places=2, default=0)

class Payment(models.Model):
    work_order = models.ForeignKey(WorkOrder, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    payment_method = models.CharField(max_length=50)
    transaction_ref = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

class Appointment(models.Model):
    garage = models.ForeignKey(Garage, on_delete=models.CASCADE)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    date = models.CharField(max_length=50)
    time = models.CharField(max_length=20)
    reason = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

# === PHASE 1 ADDITIONS ===

class UserRole(models.Model):
    """Extends Django User with role for multi-garage access"""
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('owner', 'Garage Owner'),
        ('manager', 'Manager'),
        ('mechanic', 'Mechanic'),
        ('receptionist', 'Receptionist'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='role_profile')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='mechanic')
    garage = models.ForeignKey(Garage, on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.role}"


class MechanicProfile(models.Model):
    """Extended profile for mechanic users"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='mechanic_profile')
    garage = models.ForeignKey(Garage, on_delete=models.CASCADE, related_name='mechanics')
    skills = models.TextField(blank=True, help_text="Comma-separated skills e.g. Engine, Brakes, Electrical")
    is_available = models.BooleanField(default=True)
    phone = models.CharField(max_length=20, blank=True)
    hire_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username} - {self.garage.name}"


class ServiceCatalog(models.Model):
    """Predefined services offered by a garage"""
    garage = models.ForeignKey(Garage, on_delete=models.CASCADE, related_name='services')
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    category = models.CharField(max_length=100, blank=True, help_text="e.g. Engine, Brakes, Electrical, Bodywork")
    base_price = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    estimated_hours = models.DecimalField(max_digits=5, decimal_places=1, default=1.0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['category', 'name']

    def __str__(self):
        return f"{self.name} - MWK {self.base_price}"


class WorkOrderService(models.Model):
    """Links services from catalog to a work order"""
    work_order = models.ForeignKey(WorkOrder, on_delete=models.CASCADE, related_name='services_used')
    service = models.ForeignKey(ServiceCatalog, on_delete=models.SET_NULL, null=True)
    custom_description = models.CharField(max_length=200, blank=True)
    quantity = models.DecimalField(max_digits=5, decimal_places=1, default=1.0)
    price = models.DecimalField(max_digits=12, decimal_places=2)

    def __str__(self):
        return f"{self.service or self.custom_description} - {self.work_order.srn}"

# === PHASE 2: RELATIONSHIPS & TRACKING ===

class WorkOrderPart(models.Model):
    """Tracks inventory parts consumed on a work order"""
    work_order = models.ForeignKey(WorkOrder, on_delete=models.CASCADE, related_name='parts_used')
    inventory_item = models.ForeignKey(InventoryItem, on_delete=models.SET_NULL, null=True)
    part_name = models.CharField(max_length=200)
    quantity_used = models.IntegerField(default=1)
    unit_price = models.DecimalField(max_digits=12, decimal_places=2)
    total_price = models.DecimalField(max_digits=12, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        self.total_price = self.quantity_used * self.unit_price
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.part_name} x{self.quantity_used} - {self.work_order.srn}"


class ServiceHistory(models.Model):
    """Records completed services for a vehicle's history"""
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name='service_history')
    work_order = models.ForeignKey(WorkOrder, on_delete=models.SET_NULL, null=True)
    garage = models.ForeignKey(Garage, on_delete=models.CASCADE)
    mechanic = models.ForeignKey(MechanicProfile, on_delete=models.SET_NULL, null=True)
    service_date = models.DateField(auto_now_add=True)
    description = models.TextField()
    mileage_at_service = models.IntegerField(default=0)
    total_cost = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-service_date']
        verbose_name_plural = 'Service Histories'

    def __str__(self):
        return f"{self.vehicle.plate} - {self.service_date}"


class DiagnosticRecord(models.Model):
    """Stores diagnostic results linked to a work order"""
    work_order = models.ForeignKey(WorkOrder, on_delete=models.CASCADE, related_name='diagnostics')
    mechanic = models.ForeignKey(MechanicProfile, on_delete=models.SET_NULL, null=True)
    symptoms = models.TextField(blank=True)
    fault_codes = models.TextField(blank=True, help_text="Comma-separated OBD2/DTC codes")
    diagnosis = models.TextField(blank=True)
    recommended_action = models.TextField(blank=True)
    estimated_cost = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Diagnosis - {self.work_order.srn}"


class Invoice(models.Model):
    """Final invoice generated from a completed work order"""
    work_order = models.OneToOneField(WorkOrder, on_delete=models.CASCADE, related_name='invoice')
    garage = models.ForeignKey(Garage, on_delete=models.CASCADE)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    invoice_number = models.CharField(max_length=20, unique=True, default=generate_ref)
    subtotal_services = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    subtotal_parts = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    tax_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    discount_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(max_length=20, choices=[('draft','Draft'),('sent','Sent'),('paid','Paid'),('cancelled','Cancelled')], default='draft')
    issued_date = models.DateField(auto_now_add=True)
    due_date = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Invoice {self.invoice_number} - {self.customer.full_name}"

# === NOTIFICATION SYSTEM ===
class Notification(models.Model):
    """In-app notifications for garage staff"""
    PRIORITY = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]
    TYPE_CHOICES = [
        ('work_order', 'Work Order'),
        ('appointment', 'Appointment'),
        ('inventory', 'Inventory'),
        ('payment', 'Payment'),
        ('system', 'System'),
    ]
    garage = models.ForeignKey(Garage, on_delete=models.CASCADE, related_name='notifications')
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='notifications')
    type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='system')
    title = models.CharField(max_length=200)
    message = models.TextField()
    priority = models.CharField(max_length=10, choices=PRIORITY, default='medium')
    is_read = models.BooleanField(default=False)
    link = models.CharField(max_length=500, blank=True, help_text="Deep link to related resource")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"[{self.priority.upper()}] {self.title} - {self.garage.name}"

class AuditLog(models.Model):
    ACTION_CHOICES = [
        ('create', 'Created'), ('update', 'Updated'), ('delete', 'Deleted'),
        ('login', 'Login'), ('logout', 'Logout'), ('view', 'Viewed'),
    ]
    garage = models.ForeignKey(Garage, on_delete=models.CASCADE, related_name='audit_logs')
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    model_name = models.CharField(max_length=100)
    object_id = models.IntegerField(null=True, blank=True)
    description = models.TextField()
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta: ordering = ['-created_at']

    def __str__(self): return f"[{self.action.upper()}] {self.model_name} - {self.user}"

