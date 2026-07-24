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
