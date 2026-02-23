from django.contrib import admin
from .models import UserProfile, Pothole, Vote, Notification


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'truth_score', 'total_reports', 'created_at')
    list_filter = ('truth_score', 'created_at')
    search_fields = ('user__username', 'user__email')


@admin.register(Pothole)
class PotholeAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'severity', 'status', 'vote_count', 'created_at')
    list_filter = ('severity', 'status', 'created_at')
    search_fields = ('user__username', 'description')
    readonly_fields = ('created_at', 'updated_at', 'vote_count')
    fieldsets = (
        ('Pothole Information', {
            'fields': ('user', 'description', 'image', 'severity')
        }),
        ('Location', {
            'fields': ('latitude', 'longitude')
        }),
        ('Status & Assignment', {
            'fields': ('status', 'assigned_worker', 'completion_image')
        }),
        ('Statistics', {
            'fields': ('vote_count', 'created_at', 'updated_at')
        }),
    )


@admin.register(Vote)
class VoteAdmin(admin.ModelAdmin):
    list_display = ('user', 'pothole', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__username', 'pothole__description')


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'notification_type', 'is_read', 'created_at')
    list_filter = ('notification_type', 'is_read', 'created_at')
    search_fields = ('user__username', 'message')
    readonly_fields = ('created_at',)
