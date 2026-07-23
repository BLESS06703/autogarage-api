from django.db import models

class Garage(models.Model):
    name = models.CharField(max_length=200)
    phone = models.CharField(max_length=20)
    address = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

class Customer(models.Model):
    garage = models.ForeignKey(Garage, on_delete=models.CASCADE, null=True)
    full_name = models.CharField(max_length=200)
    phone = models.CharField(max_length=20)
    reference_number = models.CharField(max_length=20, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

class WorkOrder(models.Model):
    garage = models.ForeignKey(Garage, on_delete=models.CASCADE, null=True)
    customer_name = models.CharField(max_length=200)
    vehicle_info = models.CharField(max_length=200)
    status = models.CharField(max_length=30, default='In Progress')
    cost_estimate = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    srn = models.CharField(max_length=20, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

class InventoryItem(models.Model):
    garage = models.ForeignKey(Garage, on_delete=models.CASCADE, null=True)
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
