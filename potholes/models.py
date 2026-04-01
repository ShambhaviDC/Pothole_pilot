from django.db import models
from django.contrib.auth.models import User
from django.utils.timezone import now

def get_ward(latitude, longitude):
    """Calculate ward number based on latitude and longitude."""
    wards = {
        1: {'lat_min': 40.7000, 'lat_max': 40.7200, 'lng_min': -74.0100, 'lng_max': -73.9900},
        2: {'lat_min': 40.7200, 'lat_max': 40.7400, 'lng_min': -74.0100, 'lng_max': -73.9900},
        3: {'lat_min': 40.7000, 'lat_max': 40.7200, 'lng_min': -73.9900, 'lng_max': -73.9700},
        4: {'lat_min': 40.7200, 'lat_max': 40.7400, 'lng_min': -73.9900, 'lng_max': -73.9700},
        5: {'lat_min': 40.7400, 'lat_max': 40.7600, 'lng_min': -74.0100, 'lng_max': -73.9900},
        6: {'lat_min': 40.7400, 'lat_max': 40.7600, 'lng_min': -73.9900, 'lng_max': -73.9700},
        7: {'lat_min': 40.6800, 'lat_max': 40.7000, 'lng_min': -74.0100, 'lng_max': -73.9900},
        8: {'lat_min': 40.6800, 'lat_max': 40.7000, 'lng_min': -73.9900, 'lng_max': -73.9700},
        9: {'lat_min': 40.7600, 'lat_max': 40.7800, 'lng_min': -74.0100, 'lng_max': -73.9900},
        10: {'lat_min': 40.7600, 'lat_max': 40.7800, 'lng_min': -73.9900, 'lng_max': -73.9700},
    }
    
    for ward_num, bounds in wards.items():
        if (bounds['lat_min'] <= latitude <= bounds['lat_max'] and
            bounds['lng_min'] <= longitude <= bounds['lng_max']):
            return ward_num
    return 1

class UserProfile(models.Model):
    """User profile model."""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    truth_score = models.IntegerField(default=0)
    total_reports = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.username} - Score: {self.truth_score}"

    @property
    def unread_notifications_count(self):
        """Return the count of unread notifications."""
        return self.user.notifications.filter(is_read=False).count()

class Pothole(models.Model):
    """Pothole report model."""
    SEVERITY_CHOICES = [
        ('Low', 'Low'),
        ('Medium', 'Medium'),
        ('High', 'High'),
    ]
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('In Progress', 'In Progress'),
        ('Fixed', 'Fixed'),
        ('Invalid', 'Invalid'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='potholes', null=True, blank=True)
    image = models.ImageField(upload_to='potholes/')
    latitude = models.FloatField()
    longitude = models.FloatField()
    ward_number = models.IntegerField(default=1)
    description = models.TextField(blank=True, null=True)
    severity = models.CharField(max_length=10, choices=SEVERITY_CHOICES, default='Medium')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    vote_count = models.IntegerField(default=0)
    assigned_worker = models.CharField(max_length=100, blank=True, null=True)
    completion_image = models.ImageField(upload_to='completion/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def save(self, *args, **kwargs):
        """Auto-calculate ward number before saving."""
        if self.latitude and self.longitude:
            self.ward_number = get_ward(self.latitude, self.longitude)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"Pothole by {self.user.username} - Ward {self.ward_number}"

class Vote(models.Model):
    """Vote model for upvoting potholes."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='votes')
    pothole = models.ForeignKey(Pothole, on_delete=models.CASCADE, related_name='votes')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('user', 'pothole')
    
    def __str__(self):
        return f"{self.user.username} voted on pothole {self.pothole.id}"

class Notification(models.Model):
    """Notification model."""
    NOTIFICATION_TYPES = [
        ('fixed', 'Fixed'),
        ('in_progress', 'In Progress'),
        ('invalid', 'Invalid'),
        ('new_vote', 'New Vote'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    pothole = models.ForeignKey(Pothole, on_delete=models.CASCADE, null=True, blank=True)
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES, default='fixed')
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Notification for {self.user.username}"