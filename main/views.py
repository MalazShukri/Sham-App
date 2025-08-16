from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from .models import Service, User, ServiceRequest
from .serializers import (
    ServiceDetailSerializer, ServiceListSerializer,
    UserRegistrationSerializer, ServiceRequestSerializer
)
from django.core.exceptions import ObjectDoesNotExist

def get_language(request):
    raw = (request.headers.get('Accept-Language') or '').lower()
    return 'ar' if raw.startswith('ar') else 'en'



@api_view(['GET'])
@permission_classes([AllowAny])
def service_list(request):
    try:
        services = Service.objects.all()
        if not services.exists():
            return Response({
                "status": False,
                "message": "No services found",
                "data": []
            }, status=status.HTTP_404_NOT_FOUND)
            
        language = get_language(request)
        serializer = ServiceListSerializer(services, many=True, context={'language': language})
        return Response({
            "status": True,
            "message": f"Successfully retrieved {services.count()} services",
            "data": serializer.data
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({
            "status": False,
            "message": str(e),
            "data": None
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([AllowAny])
def service_detail(request, service_id):
    """API endpoint that returns a specific service with all fields including details"""
    try:
        service = Service.objects.get(id=service_id)
        language = get_language(request)
        serializer = ServiceDetailSerializer(service, context={'language': language})
        return Response({
            "status": True,
            "message": f"Successfully retrieved service with ID {service_id}",
            "data": serializer.data
        }, status=status.HTTP_200_OK)
    except ObjectDoesNotExist:
        return Response({
            "status": False,
            "message": f"Service with ID {service_id} not found",
            "data": None
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({
            "status": False,
            "message": str(e),
            "data": None
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



@api_view(['GET'])
def list_service_requests(request):
    """API endpoint for listing service requests"""
    try:
        user = request.user
        if not user or not user.is_authenticated:
            return Response({
                "status": False,
                "message": "Authentication credentials were not provided or invalid.",
                "data": None
            }, status=status.HTTP_401_UNAUTHORIZED)

        service_requests = ServiceRequest.objects.filter(user=user)
        if not service_requests.exists():
            return Response({
                "status": False,
                "message": "No service requests found",
                "data": []
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = ServiceRequestSerializer(service_requests, many=True)
        return Response({
            "status": True,
            "message": f"Successfully retrieved {service_requests.count()} service requests",
            "data": serializer.data
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({
            "status": False,
            "message": str(e),
            "data": None
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([AllowAny])
def register_user(request):
    """
    Registers user and returns a token.
    Your current rule sets password == phone_number. Kept as-is.
    """
    try:
        s = UserRegistrationSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        user = s.save()

        # rotate token on register
        Token.objects.filter(user=user).delete()
        token = Token.objects.create(user=user)

        return Response({
            "status": True,
            "message": "User registered",
            "data": {
                "id": s.data.id,
                "full_name": s.data.full_name,
                "phone_number": s.data.phone_number,
                "token": token.key
            }
        }, status=status.HTTP_201_CREATED)
    except Exception as e:
        return Response({"status": False, "message": str(e), "data": None},
                        status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def token_login(request):
    """
    Login by full_name + password (password = phone_number in your current logic).
    Returns a fresh token (old one is deleted).
    """
    full_name = request.data.get('full_name')
    password = request.data.get('password')
    if not full_name or not password:
        return Response({"status": False, "message": "full_name and password are required", "data": None},
                        status=status.HTTP_400_BAD_REQUEST)

    user = authenticate(request, full_name=full_name, password=password)
    if not user:
        return Response({"status": False, "message": "Invalid credentials", "data": None},
                        status=status.HTTP_401_UNAUTHORIZED)

    Token.objects.filter(user=user).delete()
    token = Token.objects.create(user=user)

    return Response({"status": True, "message": "Login successful", "data": {"token": token.key}})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def token_logout(request):
    Token.objects.filter(user=request.user).delete()
    return Response({"status": True, "message": "Logged out", "data": None})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_service_request(request):
    try:
        data = request.data.copy()
        data['user'] = request.user.id
        ser = ServiceRequestSerializer(
            data=data, context={'language': get_language(request)})
        if ser.is_valid():
            obj = ser.save()
            return Response({"status": True, "message": "Created", "data": ServiceRequestSerializer(obj, context={'language': get_language(request)}).data},
                            status=status.HTTP_201_CREATED)
        return Response({"status": False, "message": ser.errors, "data": None}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({"status": False, "message": str(e), "data": None},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR)
