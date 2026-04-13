from django.core.management.base import BaseCommand
from potholes.models import Pothole

class Command(BaseCommand):
    help = 'Deletes images of potholes that have been fixed for more than 7 days.'

    def handle(self, *args, **kwargs):
        from django.utils.timezone import now
        from datetime import timedelta
        from django.db.models import Q
        
        seven_days_ago = now() - timedelta(days=7)
        potholes = Pothole.objects.filter(
            status='Fixed', 
            image__isnull=False
        ).filter(Q(fixed_at__lte=seven_days_ago) | Q(fixed_at__isnull=True, updated_at__lte=seven_days_ago))
        
        count = 0
        for pothole in potholes:
            pothole.cleanup_old_images()
            if not pothole.image:
                count += 1
        
        self.stdout.write(self.style.SUCCESS(f'Successfully cleaned up {count} images.'))
