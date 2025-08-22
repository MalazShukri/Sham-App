from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.models import Token
from django.core.exceptions import ObjectDoesNotExist
from .models import Service, User, ServiceRequest
from .serializers import (
    ServiceDetailSerializer, ServiceListSerializer,
    UserRegistrationSerializer, ServiceRequestSerializer
)
from django.db import IntegrityError


def get_language(request):
    raw = (request.headers.get('Accept-Language') or '').lower()
    return 'ar' if raw.startswith('ar') else 'en'


@api_view(['GET'])
@permission_classes([AllowAny])
def service_list(request):
    services = Service.objects.all()
    if not services.exists():
        return Response({"status": False, "message": "No services found", "data": []}, status=404)
    ser = ServiceListSerializer(services, many=True, context={
                                'language': get_language(request)})
    return Response({"status": True, "message": f"Successfully retrieved {services.count()} services", "data": ser.data})


@api_view(['GET'])
@permission_classes([AllowAny])
def service_detail(request, service_id):
    try:
        service = Service.objects.get(id=service_id)
    except ObjectDoesNotExist:
        return Response({"status": False, "message": f"Service with ID {service_id} not found", "data": None}, status=404)
    ser = ServiceDetailSerializer(
        service, context={'language': get_language(request)})
    return Response({"status": True, "message": f"Successfully retrieved service with ID {service_id}", "data": ser.data})


@api_view(['GET'])
@permission_classes([IsAuthenticated])                
def list_service_requests(request):
    qs = ServiceRequest.objects.filter(user=request.user)
    if not qs.exists():
        return Response({"status": False, "message": "No service requests found", "data": []}, status=404)
    ser = ServiceRequestSerializer(qs, many=True, context={
                                   'language': get_language(request)})
    return Response({"status": True, "message": f"Successfully retrieved {qs.count()} service requests", "data": ser.data})


@api_view(['POST'])
@permission_classes([AllowAny])
def register_user(request):
    s = UserRegistrationSerializer(data=request.data)
    s.is_valid(raise_exception=True)
    try:
        user = s.save()

    except IntegrityError:
        return Response({
            "status": False,
            "message": "This full_name already exists",
            "data": None
        }, status=400)
    Token.objects.filter(user=user).delete()
    token = Token.objects.create(user=user)
    return Response({
        "status": True,
        "message": "User registered",
        "data": {
            "id": s.data["id"],
            "full_name": s.data["full_name"],
            "phone_number": s.data["phone_number"],
            "token": token.key
        }
    }, status=201)


@api_view(['POST'])
@permission_classes([AllowAny])
def token_login(request):
    full_name = (request.data.get('full_name') or '').strip()
    phone_number = (request.data.get('phone_number') or '').strip()
    if not full_name or not phone_number:
        return Response({"status": False, "message": "full_name and phone_number are required", "data": None}, status=400)

    try:
        user = User.objects.get(full_name=full_name, phone_number=phone_number)
    except User.DoesNotExist:
        return Response({"status": False, "message": "Invalid credentials", "data": None}, status=401)

    if not user.check_password(phone_number):
        return Response({"status": False, "message": "Invalid credentials", "data": None}, status=401)

    Token.objects.filter(user=user).delete()
    token = Token.objects.create(user=user)
    return Response({"status": True, "message": "Login successful", "data": {
        "id": user.id, "full_name": user.full_name, "phone_number": user.phone_number, "token": token.key
    }}, status=200)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def token_logout(request):
    Token.objects.filter(user=request.user).delete()
    return Response({"status": True, "message": "Logged out", "data": None})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_service_request(request):
    ser = ServiceRequestSerializer(
        data=request.data,
        context={'request': request, 'language': get_language(request)}
    )
    ser.is_valid(raise_exception=True)
    obj = ser.save(user=request.user)    
    return Response({
        "status": True,
        "message": "Created",
        "data": ServiceRequestSerializer(obj, context={'language': get_language(request)}).data
    }, status=201)
