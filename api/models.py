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
