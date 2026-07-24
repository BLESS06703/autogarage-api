from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import WorkOrder, InventoryItem, Appointment, Payment, Notification
from .views import send_notification


@receiver(post_save, sender=WorkOrder)
def notify_work_order(sender, instance, created, **kwargs):
    """Notify on new work order or status change"""
    if created:
        send_notification(
            instance.garage,
            'work_order',
            f'New Work Order #{instance.srn}',
            f'Vehicle: {instance.vehicle} - {instance.issue_description[:100]}',
            'medium',
            link=f'/work-orders/{instance.id}'
        )
    elif instance.status == 'Completed':
        send_notification(
            instance.garage,
            'work_order',
            f'Work Order Completed #{instance.srn}',
            f'Job completed. Ready for invoicing.',
            'high',
            link=f'/work-orders/{instance.id}'
        )
    elif instance.status == 'Awaiting Parts':
        send_notification(
            instance.garage,
            'work_order',
            f'Parts Needed #{instance.srn}',
            f'Work order is awaiting parts.',
            'high',
            link=f'/inventory/'
        )


@receiver(post_save, sender=InventoryItem)
def notify_low_stock(sender, instance, **kwargs):
    """Notify when stock drops below threshold"""
    if instance.quantity < instance.min_threshold:
        send_notification(
            instance.garage,
            'inventory',
            f'Low Stock: {instance.part_name}',
            f'Only {instance.quantity} remaining (min: {instance.min_threshold})',
            'urgent',
            link=f'/inventory/'
        )


@receiver(post_save, sender=Appointment)
def notify_appointment(sender, instance, created, **kwargs):
    """Notify on new appointment"""
    if created:
        send_notification(
            instance.garage,
            'appointment',
            f'New Appointment',
            f'{instance.customer} - {instance.date} at {instance.time}: {instance.reason}',
            'low',
            link=f'/appointments/'
        )


@receiver(post_save, sender=Payment)
def notify_payment(sender, instance, created, **kwargs):
    """Notify on payment received"""
    if created:
        send_notification(
            instance.work_order.garage,
            'payment',
            f'Payment Received',
            f'MWK {instance.amount:,.2f} via {instance.payment_method}',
            'medium',
            link=f'/payments/'
        )
