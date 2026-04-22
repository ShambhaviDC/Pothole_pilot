from django.urls import path
from . import views

urlpatterns = [
    # Public pages
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    
    # User portal
    path('dashboard/', views.user_dashboard, name='user_dashboard'),
    path('profile/', views.user_profile, name='user_profile'),
    path('report/', views.report_pothole, name='report_pothole'),
    path('feed/', views.community_feed, name='community_feed'),
    path('pothole/<int:pothole_id>/', views.pothole_detail, name='pothole_detail'),
    path('notifications/', views.notifications, name='notifications'),
    path('notification/<int:notification_id>/read/', views.mark_notification_as_read, name='mark_notification_read'),
    
    # Map view
    path('map/', views.map_view, name='map_view'),
    path('api/potholes/', views.potholes_api, name='potholes_api'),
    
    # Voting
    path('pothole/<int:pothole_id>/upvote/', views.upvote_pothole, name='upvote_pothole'),
    path('api/stats/', views.get_pothole_stats, name='get_pothole_stats'),
    
    # Admin portal (Municipality)
    path('municipality/dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('municipality/pothole/<int:pothole_id>/update/', views.update_pothole_status, name='update_pothole'),
    path('municipality/potholes/delete-old/', views.delete_old_potholes, name='delete_old_potholes'),
]
