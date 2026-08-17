from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, BasePermission
from rest_framework.response import Response
from api.models import Customer, Vehicle, WorkOrder, InventoryItem, UserRole, MechanicProfile
from api.views import get_user_garage

class CanManageStaff(BasePermission):
    """
    Only owners, admins and managers can create/list staff.
    """

    allowed_roles = ['owner', 'admin', 'manager']

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        if request.user.is_superuser:
            return True

        garage = get_user_garage(request.user)

        if not garage:
            return False

        try:
            role = UserRole.objects.get(
                user=request.user,
                garage=garage
            )
            return role.role in self.allowed_roles
        except UserRole.DoesNotExist:
            return False


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def quick_intake(request):
    """Create customer + vehicle + work order in one call"""
    garage = get_user_garage(request.user)
    if not garage:
        return Response({'error': 'No garage assigned'}, status=403)
    
    data = request.data
    
    # 1. Create customer
    name = data.get('customer_name', '').strip()
    phone = data.get('customer_phone', '').strip()
    if not name or not phone:
        return Response({'error': 'Customer name and phone required'}, status=400)
    
    customer, _ = Customer.objects.get_or_create(
        full_name=name, phone=phone, garage=garage,
        defaults={'email': data.get('customer_email', '')}
    )
    
    # 2. Create vehicle
    make = data.get('vehicle_make', '').strip()
    model = data.get('vehicle_model', '').strip()
    plate = data.get('vehicle_plate', '').strip()
    year = data.get('vehicle_year', '').strip()
    
    if make and model and plate and year:
        vehicle, _ = Vehicle.objects.get_or_create(
            plate=plate, garage=garage,
            defaults={
                'customer': customer,
                'make': make,
                'model_name': model,
                'year': year,
                'mileage': int(data.get('vehicle_mileage', 0))
            }
        )
    else:
        vehicle = None
    
    # 3. Create work order
    issue = data.get('issue_description', '').strip()
    cost = data.get('cost_estimate', 0)
    
    wo = None
    if issue and vehicle:
        wo = WorkOrder.objects.create(
            vehicle=vehicle,
            garage=garage,
            issue_description=issue,
            cost_estimate=float(cost) if cost else 0,
            status='In Progress'
        )
    
    return Response({
        'message': 'Intake complete',
        'customer_id': customer.id,
        'customer_name': customer.full_name,
        'vehicle_id': vehicle.id if vehicle else None,
        'plate': vehicle.plate if vehicle else None,
        'work_order_id': wo.id if wo else None,
        'srn': wo.srn if wo else None
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def quick_customer(request):
    """Create just a customer"""
    garage = get_user_garage(request.user)
    if not garage:
        return Response({'error': 'No garage'}, status=403)
    
    name = request.data.get('full_name', '').strip()
    phone = request.data.get('phone', '').strip()
    
    if not name or not phone:
        return Response({'error': 'Name and phone required'}, status=400)
    
    customer = Customer.objects.create(
        full_name=name,
        phone=phone,
        email=request.data.get('email', ''),
        garage=garage
    )
    return Response({
        'id': customer.id,
        'full_name': customer.full_name,
        'phone': customer.phone,
        'reference_number': customer.reference_number
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def quick_vehicle(request):
    """Create a vehicle with customer lookup"""
    garage = get_user_garage(request.user)
    if not garage:
        return Response({'error': 'No garage'}, status=403)
    
    make = request.data.get('make', '').strip()
    model = request.data.get('model_name', '').strip()
    plate = request.data.get('plate', '').strip()
    year = request.data.get('year', '').strip()
    customer_id = request.data.get('customer_id')
    
    if not all([make, model, plate, year]):
        return Response({'error': 'Make, model, plate, year required'}, status=400)
    
    # Find or create customer
    customer = None
    if customer_id:
        try:
            customer = Customer.objects.get(id=customer_id, garage=garage)
        except Customer.DoesNotExist:
            pass
    
    if not customer:
        return Response({'error': 'Valid customer_id required'}, status=400)
    
    vehicle = Vehicle.objects.create(
        make=make, model_name=model, plate=plate, year=year,
        customer=customer, garage=garage,
        mileage=int(request.data.get('mileage', 0))
    )
    return Response({'id': vehicle.id, 'plate': vehicle.plate, 'make': vehicle.make, 'model_name': vehicle.model_name})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def quick_workorder(request):
    """Create a work order with vehicle lookup by plate"""
    garage = get_user_garage(request.user)
    if not garage:
        return Response({'error': 'No garage'}, status=403)
    
    plate = request.data.get('plate', '').strip()
    issue = request.data.get('issue_description', '').strip()
    cost = request.data.get('cost_estimate', 0)
    customer_name = request.data.get('customer_name', '').strip()
    customer_phone = request.data.get('customer_phone', '').strip()
    
    if not plate or not issue:
        return Response({'error': 'Plate and issue required'}, status=400)
    
    # Find or create vehicle
    try:
        vehicle = Vehicle.objects.get(plate=plate, garage=garage)
    except Vehicle.DoesNotExist:
        # Create customer first
        if customer_name and customer_phone:
            customer, _ = Customer.objects.get_or_create(
                full_name=customer_name, phone=customer_phone, garage=garage
            )
        else:
            return Response({'error': 'Vehicle not found. Provide customer_name and customer_phone to register it.'}, status=400)
        
        vehicle = Vehicle.objects.create(
            plate=plate, garage=garage, customer=customer,
            make=request.data.get('make', 'Unknown'),
            model_name=request.data.get('model_name', 'Unknown'),
            year=request.data.get('year', '2024'),
            mileage=int(request.data.get('mileage', 0))
        )
    
    wo = WorkOrder.objects.create(
        vehicle=vehicle, garage=garage,
        issue_description=issue,
        cost_estimate=float(cost) if cost else 0,
        status='In Progress'
    )
    return Response({
        'id': wo.id, 'srn': wo.srn,
        'vehicle_plate': vehicle.plate,
        'status': wo.status
    })
import qrcode, io, base64
from django.http import JsonResponse

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def qr_code(request, srn):
    """Generate QR code for a work order"""
    garage = get_user_garage(request.user)
    if not garage: return Response({'error': 'No garage'}, status=403)
    
    try:
        wo = WorkOrder.objects.get(srn=srn, garage=garage)
    except WorkOrder.DoesNotExist:
        return Response({'error': 'Not found'}, status=404)
    
    qr = qrcode.QRCode(version=1, box_size=10, border=4)
    qr.add_data(f"WO:{wo.srn}|Vehicle:{wo.vehicle}|Status:{wo.status}|Cost:{wo.cost_estimate}")
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    
    buf = io.BytesIO()
    img.save(buf, format='PNG')
    buf.seek(0)
    img_b64 = base64.b64encode(buf.read()).decode()
    
    return Response({'srn': wo.srn, 'qr_code': img_b64, 'status': wo.status, 'vehicle': str(wo.vehicle)})

@api_view(['POST'])
@permission_classes([CanManageStaff])
def add_staff(request):
    """Add a mechanic or staff member"""
    from django.contrib.auth.models import User
    garage = get_user_garage(request.user)
    if not garage:
        return Response({'error': 'No garage'}, status=403)
    
    username = request.data.get('username', '').strip()
    password = request.data.get('password', '').strip()
    full_name = request.data.get('full_name', '').strip()
    role = request.data.get('role', 'mechanic').strip()
    skills = request.data.get('skills', '').strip()

    allowed_roles = {
        'admin',
        'manager',
        'mechanic',
        'receptionist',
    }

    if role not in allowed_roles:
        return Response(
            {
                'error': (
                    'Invalid role. Choose from: '
                    + ', '.join(sorted(allowed_roles))
                )
            },
            status=400
        )
    phone = request.data.get('phone', '').strip()
    
    if not username or not password:
        return Response({'error': 'Username and password required'}, status=400)
    
    if User.objects.filter(username=username).exists():
        return Response({'error': 'Username already exists'}, status=400)
    
    user = User.objects.create_user(username=username, password=password)
    if full_name:
        name_parts = full_name.split(' ', 1)
        user.first_name = name_parts[0]
        if len(name_parts) > 1:
            user.last_name = name_parts[1]
        user.save()
    
    # Assign role
    UserRole.objects.create(user=user, role=role, garage=garage)
    
    # Create mechanic profile if role is mechanic
    if role == 'mechanic':
        MechanicProfile.objects.create(
            user=user, garage=garage,
            skills=skills, phone=phone, is_available=True
        )
    
    return Response({
        'message': f'{role.title()} created',
        'user_id': user.id,
        'username': user.username,
        'role': role
    })

@api_view(['GET'])
@permission_classes([CanManageStaff])
def list_users(request):
    """List all users/staff for the garage"""
    garage = get_user_garage(request.user)
    if not garage:
        return Response({'error': 'No garage'}, status=403)
    
    roles = UserRole.objects.filter(garage=garage).select_related('user')
    users = []
    for r in roles:
        users.append({
            'id': r.user.id,
            'username': r.user.username,
            'full_name': r.user.get_full_name() or r.user.username,
            'role': r.role,
            'is_active': r.user.is_active,
            'date_joined': r.user.date_joined.strftime('%Y-%m-%d')
        })
    return Response(users)

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def scan_vehicle(request):
    garage = get_user_garage(request.user)
    if not garage: return Response({"error": "No garage"}, status=403)
    plate = request.data.get("plate", "").strip().upper()
    if not plate: return Response({"error": "Plate required"}, status=400)
    try:
        v = Vehicle.objects.get(plate=plate, garage=garage)
        return Response({"found": True, "id": v.id, "plate": v.plate, "make": v.make, "model_name": v.model_name, "year": v.year, "mileage": v.mileage, "customer_name": v.customer.full_name, "customer_phone": v.customer.phone})
    except Vehicle.DoesNotExist:
        return Response({"found": False, "plate": plate, "message": "Not found"})


import uuid
from django.core.files.storage import default_storage
from django.conf import settings

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def upload_file(request):
    """Upload a file (vehicle photo, document, etc.)"""
    garage = get_user_garage(request.user)
    if not garage:
        return Response({'error': 'No garage'}, status=403)
    
    uploaded = request.FILES.get('file')
    if not uploaded:
        return Response({'error': 'No file provided'}, status=400)
    
    # Validate file type
    allowed = ['image/jpeg', 'image/png', 'image/webp', 'application/pdf']
    if uploaded.content_type not in allowed:
        return Response({'error': f'File type {uploaded.content_type} not allowed. Use JPEG, PNG, WebP, or PDF.'}, status=400)
    
    # Validate size (max 10MB)
    if uploaded.size > 10 * 1024 * 1024:
        return Response({'error': 'File too large. Maximum 10MB.'}, status=400)
    
    # Generate unique filename
    ext = uploaded.name.split('.')[-1] if '.' in uploaded.name else 'file'
    filename = f"{garage.id}/{uuid.uuid4().hex}.{ext}"
    
    # Save file
    path = default_storage.save(f'uploads/{filename}', uploaded)
    url = f"{settings.MEDIA_URL}{path}"
    
    # Optionally save reference in GarageFile model
    file_type = 'image' if uploaded.content_type.startswith('image/') else 'document'
    GarageFile.objects.create(
        garage=garage,
        uploaded_by=request.user,
        filename=uploaded.name,
        file_type=file_type,
        size=uploaded.size
    )
    
    return Response({
        'message': 'File uploaded',
        'filename': uploaded.name,
        'url': request.build_absolute_uri(url),
        'size': uploaded.size,
        'type': file_type
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_files(request):
    """List files for the garage"""
    garage = get_user_garage(request.user)
    if not garage:
        return Response({'error': 'No garage'}, status=403)
    
    files = GarageFile.objects.filter(garage=garage).order_by('-uploaded_at')[:50]
    return Response([{
        'id': f.id,
        'filename': f.filename,
        'file_type': f.file_type,
        'size': f.size,
        'uploaded_at': f.uploaded_at.strftime('%Y-%m-%d %H:%M'),
        'uploaded_by': f.uploaded_by.username if f.uploaded_by else None
    } for f in files])

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_cart(request):
    garage = get_user_garage(request.user)
    if not garage: return Response({'error': 'No garage'}, status=403)
    customer_id = request.query_params.get('customer_id')
    if not customer_id: return Response({'error': 'customer_id required as query param'}, status=400)
    try:
        customer = Customer.objects.get(id=customer_id, garage=garage)
        cart, _ = Cart.objects.get_or_create(customer=customer, is_checked_out=False, defaults={'garage': garage})
        return Response(CartSerializer(cart).data)
    except Customer.DoesNotExist:
        return Response({'error': 'Customer not found'}, status=404)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_to_cart(request):
    garage = get_user_garage(request.user)
    if not garage: return Response({'error': 'No garage'}, status=403)
    customer_id = request.data.get('customer_id')
    inventory_id = request.data.get('inventory_id')
    quantity = int(request.data.get('quantity', 1))
    if not customer_id or not inventory_id: return Response({'error': 'customer_id and inventory_id required'}, status=400)
    try:
        customer = Customer.objects.get(id=customer_id, garage=garage)
        inv_item = InventoryItem.objects.get(id=inventory_id, garage=garage)
    except: return Response({'error': 'Not found'}, status=404)
    cart, _ = Cart.objects.get_or_create(customer=customer, is_checked_out=False, defaults={'garage': garage})
    cart_item, created = CartItem.objects.get_or_create(cart=cart, inventory_item=inv_item, defaults={'quantity': quantity, 'unit_price': inv_item.unit_price})
    if not created: cart_item.quantity += quantity; cart_item.save()
    return Response(CartSerializer(cart).data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def remove_from_cart(request):
    garage = get_user_garage(request.user)

    if not garage:
        return Response({'error': 'No garage'}, status=403)

    item_id = request.data.get('item_id')

    if not item_id:
        return Response(
            {'error': 'item_id required'},
            status=400
        )

    deleted, _ = CartItem.objects.filter(
        id=item_id,
        cart__garage=garage
    ).delete()

    if not deleted:
        return Response(
            {'error': 'Cart item not found'},
            status=404
        )

    return Response({'message': 'Removed'})

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def checkout(request):
    garage = get_user_garage(request.user)
    if not garage: return Response({'error': 'No garage'}, status=403)
    cart_id = request.data.get('cart_id')
    payment_method = request.data.get('payment_method', 'Cash')
    if not cart_id: return Response({'error': 'cart_id required'}, status=400)
    try: cart = Cart.objects.get(id=cart_id, garage=garage, is_checked_out=False)
    except: return Response({'error': 'Cart not found'}, status=404)
    total = sum(float(item.total_price) for item in cart.items.all())
    order = Order.objects.create(cart=cart, customer=cart.customer, garage=garage, total_amount=total, payment_method=payment_method, payment_status='pending')
    cart.is_checked_out = True; cart.save()
    for item in cart.items.all():
        item.inventory_item.quantity -= item.quantity
        item.inventory_item.save()
    Payment.objects.create(work_order=None, amount=total, payment_method=payment_method, transaction_ref=f'ORD-{order.id}')
    return Response(OrderSerializer(order).data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_orders(request):
    garage = get_user_garage(request.user)
    if not garage: return Response({'error': 'No garage'}, status=403)
    orders = Order.objects.filter(garage=garage).order_by('-created_at')
    return Response(OrderSerializer(orders, many=True).data)
