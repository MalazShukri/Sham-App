from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
import secrets
import uuid

# Create your models here.

class CustomUserManager(BaseUserManager):
    def create_user(self, full_name, phone_number, password=None, **extra_fields):
        if not full_name:
            raise ValueError('Full name is required')
        if not phone_number:
            raise ValueError('Phone number is required')
            
        user = self.model(
            full_name=full_name,
            phone_number=phone_number,
            **extra_fields
        )
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        user.save()
        return user

    def create_superuser(self, full_name, phone_number, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(full_name, phone_number, password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
    full_name = models.CharField(max_length=255, unique=True)
    phone_number = models.CharField(max_length=17, unique=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)

    objects = CustomUserManager()

    USERNAME_FIELD = 'full_name'
    REQUIRED_FIELDS = ['phone_number']

    def __str__(self):
        return self.full_name



class Service(models.Model):
    title = models.CharField(max_length=200)
    title_ar = models.CharField(max_length=200)
    description = models.TextField()
    description_ar = models.TextField()
    price = models.TextField()
    price_ar = models.TextField()
    image = models.ImageField(upload_to='services/')
    details = models.TextField(blank=True)
    details_ar = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title_ar

    class Meta:
        ordering = ['-created_at']



class ServiceRequest(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='service_requests')
    services = models.ManyToManyField(Service, related_name='requests')
    phone_number = models.CharField(max_length=17)
    address = models.TextField()
    service_day = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    details = models.TextField(null=True, blank=True)


    def __str__(self):
        return f"{self.user.full_name} - {self.service_day} - Services: {[s.title for s in self.services.all()]}"

    class Meta:
        ordering = ['-created_at']
