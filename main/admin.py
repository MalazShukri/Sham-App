from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Service, ServiceRequest

# Register your models here.

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('full_name', 'phone_number', 'is_staff')
    search_fields = ('full_name', 'phone_number')
    ordering = ('full_name',)
    
    # Override the fieldsets to prioritize full_name
    fieldsets = (
        (None, {'fields': ('full_name', 'phone_number', 'password')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
    )
    
    # Override the add_fieldsets to prioritize full_name
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('full_name', 'phone_number', 'password1', 'password2', 'is_staff', 'is_active', 'is_superuser',),
        }),
    )

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('title_ar', 'created_at')
    search_fields = ('title',)
    ordering = ('-created_at',)

@admin.register(ServiceRequest)
class ServiceRequestAdmin(admin.ModelAdmin):
    list_display = ('get_username', 'get_service_title', 'service_day', 'created_at')
    search_fields = ('user__full_name', 'service__title', 'location')
    list_filter = ('created_at',)
    ordering = ('-created_at',)
    readonly_fields = ('display_requested_services',)  # Add this line

    def get_username(self, obj):
        return obj.user.full_name
    get_username.short_description = 'Full Name'

    def get_service_title(self, obj):
        return ", ".join([service.title_ar for service in obj.services.all()])
    get_service_title.short_description = 'Services'

    def display_requested_services(self, obj):
        return ", ".join([service.title_ar for service in obj.services.all()])
    display_requested_services.short_description = 'Requested Services'
