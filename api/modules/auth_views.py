from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken

@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    username = request.POST.get('username', request.data.get('username', ''))
    password = request.POST.get('password', request.data.get('password', ''))
    full_name = request.POST.get('full_name', request.data.get('full_name', ''))
    email = request.POST.get('email', request.data.get('email', ''))
    
    if not username or not password:
        return Response({'error': 'Username and password required'}, status=400)
    
    if User.objects.filter(username=username).exists():
        return Response({'error': 'Username exists'}, status=400)
    
    user = User.objects.create_user(username=username, password=password, email=email, first_name=full_name)
    refresh = RefreshToken.for_user(user)
    return Response({'message': 'Registered', 'user_id': user.id, 'username': user.username, 'access': str(refresh.access_token), 'refresh': str(refresh)})

@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    from django.contrib.auth import authenticate
    username = request.POST.get('username', request.data.get('username', ''))
    password = request.POST.get('password', request.data.get('password', ''))
    
    if not username or not password:
        return Response({'error': 'Username and password required'}, status=400)
    
    user = authenticate(username=username, password=password)
    if user:
        refresh = RefreshToken.for_user(user)
        return Response({'user_id': user.id, 'username': user.username, 'access': str(refresh.access_token), 'refresh': str(refresh)})
    return Response({'error': 'Invalid credentials'}, status=401)

@api_view(['GET'])
def profile(request):
    user = request.user
    return Response({'id': user.id, 'username': user.username, 'email': user.email, 'full_name': user.first_name})
