from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from main.models import Service
import requests
from decimal import Decimal

class Command(BaseCommand):
    help = 'Add initial services to the database'

    def handle(self, *args, **kwargs):
        services_data = [
            {
                'image': 'https://cdn.prod.website-files.com/647888ca92d03e3fca3f1ea0/647888ca92d03e3fca3f2389_carpentry.jpg',
                'title': 'Carpenter workshop',
                'description': 'Professional carpentry services for all your woodworking needs.',
                'price': Decimal('10.00'),
            },
            {
                'image': 'https://facts.net/wp-content/uploads/2023/09/20-astonishing-facts-about-blacksmith-1695739626.jpg',
                'title': 'BlackSmith workshop',
                'description': 'Expert blacksmith services for metal work and repairs.',
                'price': Decimal('10.00'),
            },
            {
                'image': 'https://learnwelding.co.za/images/painting.webp',
                'title': 'Painter workshop',
                'description': 'Professional painting services for interior and exterior work.',
                'price': Decimal('10.00'),
            },
            {
                'image': 'https://img.freepik.com/free-photo/man-electrical-technician-working-switchboard-with-fuses_169016-24062.jpg',
                'title': 'Electrical workshop',
                'description': 'Professional electrical services for all your electrical needs.',
                'price': Decimal('10.00'),
            },
        ]

        for service_data in services_data:
            # Download the image
            image_url = service_data.pop('image')
            response = requests.get(image_url)
            
            if response.status_code == 200:
                # Create the service
                service = Service(**service_data)
                
                # Save the image
                image_name = image_url.split('/')[-1]
                service.image.save(
                    image_name,
                    ContentFile(response.content),
                    save=False
                )
                
                # Save the service
                service.save()
                self.stdout.write(
                    self.style.SUCCESS(f'Successfully created service: {service.title}')
                )
