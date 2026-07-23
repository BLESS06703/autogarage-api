from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken

@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    data = request.data or request.POST
    username = data.get('username', '')
    password = data.get('password', '')
    
    if not username or not password:
        return Response({'error': 'Username and password required', 'received': str(data)}, status=400)
    
    if User.objects.filter(username=username).exists():
        return Response({'error': 'Username exists'}, status=400)
    
    user = User.objects.create_user(username=username, password=password, email=data.get('email',''), first_name=data.get('full_name',''))
    refresh = RefreshToken.for_user(user)
    return Response({'message': 'Registered', 'user_id': user.id, 'username': user.username, 'access': str(refresh.access_token)})

@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    data = request.data or request.POST
    from django.contrib.auth import authenticate
    
    username = data.get('username', '')
    password = data.get('password', '')
    
    if not username or not password:
        return Response({'error': 'Username and password required'}, status=400)
    
    user = authenticate(username=username, password=password)
    if user:
        refresh = RefreshToken.for_user(user)
        return Response({'user_id': user.id, 'username': user.username, 'access': str(refresh.access_token)})
    return Response({'error': 'Invalid credentials'}, status=401)

@api_view(['GET'])
def profile(request):
    return Response({'id': request.user.id, 'username': request.user.username})
