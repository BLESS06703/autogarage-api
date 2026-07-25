from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from api.models import Customer, Vehicle, WorkOrder
from api.views import get_user_garage

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def quick_intake(request):
    """Create customer + vehicle + work order in one go"""
    garage = get_user_garage(request.user)
    if not garage:
        return Response({'error': 'No garage assigned'}, status=403)
    
    data = request.data
    
    # 1. Create or get customer
    customer_name = data.get('customer_name', '').strip()
    customer_phone = data.get('customer_phone', '').strip()
    customer_email = data.get('customer_email', '').strip()
    
    if not customer_name:
        return Response({'error': 'Customer name required'}, status=400)
    
    customer, created = Customer.objects.get_or_create(
        full_name=customer_name,
        phone=customer_phone,
        garage=garage,
        defaults={'email': customer_email}
    )
    
    # 2. Create vehicle
    vehicle_make = data.get('vehicle_make', '').strip()
    vehicle_model = data.get('vehicle_model', '').strip()
    vehicle_plate = data.get('vehicle_plate', '').strip()
    vehicle_year = data.get('vehicle_year', '').strip()
    vehicle_mileage = data.get('vehicle_mileage', 0)
    
    if vehicle_plate:
        vehicle, _ = Vehicle.objects.get_or_create(
            plate=vehicle_plate,
            garage=garage,
            defaults={
                'customer': customer,
                'make': vehicle_make,
                'model_name': vehicle_model,
                'year': vehicle_year or '',
                'mileage': int(vehicle_mileage) if vehicle_mileage else 0
            }
        )
    else:
        vehicle = None
    
    # 3. Create work order
    issue = data.get('issue_description', '').strip()
    cost = data.get('cost_estimate', 0)
    
    if issue and vehicle:
        wo = WorkOrder.objects.create(
            vehicle=vehicle,
            garage=garage,
            issue_description=issue,
            cost_estimate=float(cost) if cost else 0,
            status='In Progress'
        )
    else:
        wo = None
    
    return Response({
        'message': 'Intake successful',
        'customer_id': customer.id,
        'customer_name': customer.full_name,
        'vehicle_id': vehicle.id if vehicle else None,
        'vehicle_plate': vehicle.plate if vehicle else None,
        'work_order_id': wo.id if wo else None,
        'work_order_srn': wo.srn if wo else None,
        'is_new_customer': created
    })
