import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sham.settings')
django.setup()

from main.models import Service

# Try to count services
try:
    count = Service.objects.all().count()
    print(f"Successfully connected to MySQL! Found {count} services.")
    
    # Print first service details
    if count > 0:
        service = Service.objects.first()
        print("\nFirst service details:")
        print(f"Title (EN): {service.title}")
        print(f"Title (AR): {service.title_ar}")
        print(f"Description (EN): {service.description}")
        print(f"Description (AR): {service.description_ar}")
except Exception as e: 
    
    
    
    
    
    print(f"Error connecting to MySQL: {str(e)}") 