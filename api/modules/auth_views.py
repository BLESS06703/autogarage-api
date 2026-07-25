import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from api.models import UserRole, Garage
from django.shortcuts import render

@csrf_exempt
def register(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST only'}, status=405)
    try:
        data = json.loads(request.body)
    except:
        data = request.POST.dict()

    username = data.get('username', '')
    password = data.get('password', '')
    garage_name = data.get('garage_name', f"{username}'s Garage")

    if not username or not password:
        return JsonResponse({'error': 'Username and password required'}, status=400)
    if User.objects.filter(username=username).exists():
        return JsonResponse({'error': 'Username already exists. Please choose a different username or login.'}, status=400)
    if Garage.objects.filter(name=garage_name).exists():
        return JsonResponse({'error': 'A garage with this name already exists.'}, status=400)

    user = User.objects.create_user(username=username, password=password)
    garage = Garage.objects.create(name=garage_name, owner=user, phone=data.get('phone', ''))
    UserRole.objects.create(user=user, role='owner', garage=garage)
    refresh = RefreshToken.for_user(user)
    return JsonResponse({
        'message': 'Registration successful',
        'access': str(refresh.access_token),
        'garage_id': garage.id, 'garage_name': garage.name, 'role': 'owner'
    })

@csrf_exempt
def login(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST only'}, status=405)
    try:
        data = json.loads(request.body)
    except:
        data = request.POST.dict()

    user = authenticate(username=data.get('username',''), password=data.get('password',''))
    if user:
        refresh = RefreshToken.for_user(user)
        role_data = {}
        try:
            role = UserRole.objects.get(user=user)
            role_data = {'role': role.role, 'garage_id': role.garage.id if role.garage else None, 'garage_name': role.garage.name if role.garage else None}
        except UserRole.DoesNotExist:
            role_data = {'role': 'unassigned', 'garage_id': None, 'garage_name': None}
        return JsonResponse({'access': str(refresh.access_token), 'username': user.username, **role_data})
    return JsonResponse({'error': 'Invalid credentials'}, status=401)

def login_page(request):
    return render(request, 'login.html')

def register_page(request):
    return render(request, 'register.html')
