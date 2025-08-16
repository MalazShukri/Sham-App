from rest_framework import serializers
from .models import Service, User, ServiceRequest

class ServiceDetailSerializer(serializers.ModelSerializer):
    """Serializer for Service model including all fields"""
    class Meta:
        model = Service
        fields = '__all__'

    def to_representation(self, instance):
        data = super().to_representation(instance)
        language = self.context.get('language', 'en')
        
        # Fields that have language versions
        language_fields = ['title', 'description', 'price', 'details']
        
        if language == 'ar':
            # For Arabic, use _ar fields and keep non-language fields
            for field in language_fields:
                if f'{field}_ar' in data:
                    data[field] = data[f'{field}_ar']
                    del data[f'{field}_ar']
        else:
            # For English, remove _ar fields
            for field in language_fields:
                if f'{field}_ar' in data:
                    del data[f'{field}_ar']
        
        return data

class ServiceListSerializer(serializers.ModelSerializer):
    """Serializer for Service model excluding details field"""
    class Meta:
        model = Service
        exclude = ('details', 'details_ar')

    def to_representation(self, instance):
        data = super().to_representation(instance)
        language = self.context.get('language', 'en')
        
        # Fields that have language versions
        language_fields = ['title', 'description', 'price']
        
        if language == 'ar':
            # For Arabic, use _ar fields and keep non-language fields
            for field in language_fields:
                if f'{field}_ar' in data:
                    data[field] = data[f'{field}_ar']
                    del data[f'{field}_ar']
        else:
            # For English, remove _ar fields
            for field in language_fields:
                if f'{field}_ar' in data:
                    del data[f'{field}_ar']
        
        return data

class UserRegistrationSerializer(serializers.ModelSerializer):
    """Serializer for user registration"""
    class Meta:
        model = User
        fields = ('id', 'full_name', 'phone_number')
        read_only_fields = ('id',)

    def validate(self, attrs):
        # Block attempts to inject forbidden fields
        forbidden_fields = ['is_staff', 'is_superuser', 'is_active']
        for field in forbidden_fields:
            if field in self.initial_data:
                raise serializers.ValidationError({field: "Not allowed."})
        return super().validate(attrs)

    def create(self, validated_data):
        # Create user with provided data
        user = User.objects.create_user(
            full_name=validated_data['full_name'],
            phone_number=validated_data['phone_number'],
            password=validated_data['phone_number']  
        )
        return user

class ServiceRequestSerializer(serializers.ModelSerializer):
    services = serializers.PrimaryKeyRelatedField(
        queryset=Service.objects.all(), many=True)
    service_titles = serializers.SerializerMethodField()
    user_name = serializers.CharField(source='user.full_name', read_only=True)

    class Meta:
        model = ServiceRequest
        fields = ['id', 'service_titles', 'user_name', 'phone_number', 'address', 'service_day', 'created_at', 'services']
        read_only_fields = ['service_titles', 'user_name', 'created_at']

    def get_service_titles(self, obj):
        language = self.context.get('language', 'en')
        if language == 'ar':
            return [service.title_ar for service in obj.services.all()]
        return [service.title for service in obj.services.all()]