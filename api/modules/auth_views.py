import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken

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
    
    if not username or not password:
        return JsonResponse({'error': 'Username and password required'}, status=400)
    
    if User.objects.filter(username=username).exists():
        return JsonResponse({'error': 'Username exists'}, status=400)
    
    user = User.objects.create_user(username=username, password=password)
    refresh = RefreshToken.for_user(user)
    return JsonResponse({'message': 'Registered', 'access': str(refresh.access_token)})

@csrf_exempt
def login(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST only'}, status=405)
    
    try:
        data = json.loads(request.body)
    except:
        data = request.POST.dict()
    
    username = data.get('username', '')
    password = data.get('password', '')
    
    user = authenticate(username=username, password=password)
    if user:
        refresh = RefreshToken.for_user(user)
        return JsonResponse({'access': str(refresh.access_token), 'username': user.username})
    return JsonResponse({'error': 'Invalid credentials'}, status=401)
