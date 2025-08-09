from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from . import views

urlpatterns = [
    path('services/', views.service_list, name='service-list'),
    path('services/<int:service_id>/', views.service_detail, name='service-detail'),
    path('register/', views.register_user, name='register-user'),
    path('service-requests/', views.list_service_requests, name='list-service-requests'),
    path('service-request/create/', views.create_service_request, name='create-service-request'),
    path('login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('login/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
