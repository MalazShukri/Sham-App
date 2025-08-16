from django.urls import path
from . import views

urlpatterns = [
    path('services/', views.service_list, name='service-list'),
    path('services/<int:service_id>/', views.service_detail, name='service-detail'),
    path('service-requests/', views.list_service_requests,
         name='list-service-requests'),
    path('service-request/create/', views.create_service_request,
         name='create-service-request'),
    
    
    path('register/', views.register_user, name='register-user'),
    path('login/', views.token_login, name='token-login'),
    path('logout/', views.token_logout, name='token-logout'),
    

]
