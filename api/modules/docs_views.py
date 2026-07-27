from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from django.shortcuts import render

@api_view(['GET'])
@permission_classes([AllowAny])
def api_docs(request):
    return render(request, 'docs.html')
