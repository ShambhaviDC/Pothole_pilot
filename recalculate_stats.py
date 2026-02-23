import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pothole_project.settings')
django.setup()

from django.contrib.auth.models import User
from potholes.models import Pothole, UserProfile

def recalculate():
    try:
        u = User.objects.get(username='simran')
        p = u.profile
        
        # Reports count
        actual_reports = u.potholes.count()
        p.total_reports = actual_reports
        
        # Truth Score calculation
        score = 0
        for pothole in u.potholes.all():
            if pothole.status == 'Fixed':
                score += 10
            elif pothole.status == 'In Progress':
                score += 5
            elif pothole.status == 'Invalid':
                score -= 10
        
        p.truth_score = score
        p.save()
        print(f"SUCCESS: Recalculated for {u.username}")
        print(f"Total Reports: {p.total_reports}")
        print(f"Truth Score: {p.truth_score}")
    except User.DoesNotExist:
        print("User 'simran' not found.")

if __name__ == "__main__":
    recalculate()
