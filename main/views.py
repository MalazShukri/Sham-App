from django.http import JsonResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError
from .models import Service, User, ServiceRequest
from .serializers import (
    ServiceDetailSerializer, ServiceListSerializer,
    UserRegistrationSerializer, ServiceRequestSerializer
)
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView



def get_language(request):
    """Helper function to get language from Accept-Language header"""
    accept_language = request.headers.get('Accept-Language', 'en').lower()
    return 'ar' if accept_language == 'ar' else 'en'


@api_view(['GET'])
def service_list(request):
    """API endpoint that returns all services without details field"""
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

@api_view(['POST'])
@permission_classes([AllowAny])
def register_user(request):
    """API endpoint for user registration"""
    try:
        # First create the user
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            token_data = {
                'full_name': request.data.get('full_name'),
                'password': request.data.get('phone_number')  # Use the same password
            }
            # Now use the same serializer as TokenObtainPairView to get tokens
            token_serializer = TokenObtainPairSerializer(data=token_data)
            if token_serializer.is_valid():
                user_data = serializer.data
                token_data = token_serializer.validated_data
                user_data['token'] = token_data['access']
                return Response({
                    "status": True,
                    "message": "User registered successfully",
                    "data": {
                        "user": user_data,
                    }
                }, status=status.HTTP_201_CREATED)
            
            return Response({
                "status": False,
                "message": "Failed to generate tokens",
                "data": None
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        return Response({
            "status": False,
            "message": serializer.errors,
            "data": None
        }, status=status.HTTP_400_BAD_REQUEST)
    except IntegrityError:
        return Response({
            "status": False,
            "message": "Username already exists",
            "data": None
        }, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({
            "status": False,
            "message": str(e),
            "data": None
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
def create_service_request(request):
    """API endpoint for creating a service request with multiple services"""
    try:
        user = request.user
        if not user or not user.is_authenticated:
            return Response({
                "status": False,
                "message": "Authentication credentials were not provided or invalid.",
                "data": None
            }, status=status.HTTP_401_UNAUTHORIZED)

        services = request.data.get('services', [])
        if not isinstance(services, list) or not services:
            return Response({
                "status": False,
                "message": "services must be a non-empty list",
                "data": None
            }, status=status.HTTP_400_BAD_REQUEST)

        data = request.data.copy()
        data['user'] = user.id

        serializer = ServiceRequestSerializer(data=data)
        if serializer.is_valid():
            service_request = serializer.save(user=user)
            service_request.services.set(services)
            return Response({
                "status": True,
                "message": "Service request created successfully",
                "data": ServiceRequestSerializer(service_request).data
            }, status=status.HTTP_201_CREATED)
        else:
            return Response({
                "status": False,
                "message": serializer.errors,
                "data": None
            }, status=status.HTTP_400_BAD_REQUEST)

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
