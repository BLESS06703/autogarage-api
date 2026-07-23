from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken

@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    data = request.data
    if User.objects.filter(username=data['username']).exists():
        return Response({'error': 'Username exists'}, status=400)
    user = User.objects.create_user(
        username=data['username'],
        password=data['password'],
        email=data.get('email', ''),
        first_name=data.get('full_name', '')
    )
    refresh = RefreshToken.for_user(user)
    return Response({
        'message': 'Registered',
        'user_id': user.id,
        'username': user.username,
        'access': str(refresh.access_token),
        'refresh': str(refresh),
    })

@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    from django.contrib.auth import authenticate
    data = request.data
    user = authenticate(username=data['username'], password=data['password'])
    if user:
        refresh = RefreshToken.for_user(user)
        return Response({
            'user_id': user.id,
            'username': user.username,
            'access': str(refresh.access_token),
            'refresh': str(refresh),
        })
    return Response({'error': 'Invalid credentials'}, status=401)

@api_view(['GET'])
def profile(request):
    user = request.user
    return Response({
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'full_name': user.first_name,
    })
