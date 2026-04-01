from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.db.models import Q, Exists, OuterRef
from django.contrib import messages
from datetime import timedelta
from django.utils.timezone import now
import json

from .models import Pothole, UserProfile, Vote, Notification
from .forms import UserRegistrationForm, UserLoginForm, PotholeReportForm, PotholeUpdateForm


def home(request):
    """Home page view."""
    context = {
        'total_potholes': Pothole.objects.count(),
        'total_fixed': Pothole.objects.filter(status='Fixed').count(),
    }
    return render(request, 'potholes/home.html', context)


def register(request):
    """User registration view."""
    if request.user.is_authenticated:
        if request.user.is_staff:
            return redirect(reverse('admin_dashboard') + '?status=Pending&severity=')
        return redirect('user_dashboard')
    
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # UserProfile is created automatically via signals
            messages.success(request, 'Account created successfully! Please log in.')
            return redirect('login')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = UserRegistrationForm()
    
    return render(request, 'potholes/register.html', {'form': form})


def user_login(request):
    """User login view."""
    if request.user.is_authenticated:
        if request.user.is_staff:
            return redirect(reverse('admin_dashboard') + '?status=Pending&severity=')
        return redirect('user_dashboard')
    
    if request.method == 'POST':
        form = UserLoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            
            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome back, {user.username}!')
                if user.is_staff:
                    return redirect(reverse('admin_dashboard') + '?status=Pending&severity=')
                return redirect('user_dashboard')
            else:
                messages.error(request, 'Invalid username or password.')
    else:
        form = UserLoginForm()
    
    return render(request, 'potholes/login.html', {'form': form})


@login_required
def user_logout(request):
    """User logout view."""
    logout(request)
    messages.success(request, 'You have been logged out.')
    return redirect('home')


@login_required
def user_dashboard(request):
    """User dashboard view."""
    user = request.user
    profile = user.profile
    user_potholes = user.potholes.all()
    unread_notifications = user.notifications.filter(is_read=False).count()
    
    context = {
        'profile': profile,
        'user_potholes': user_potholes,
        'unread_notifications': unread_notifications,
    }
    return render(request, 'potholes/user_dashboard.html', context)


@login_required
def user_profile(request):
    """User profile view."""
    profile = request.user.profile
    total_votes = Vote.objects.filter(pothole__user=request.user).count()
    
    context = {
        'profile': profile,
        'total_votes': total_votes,
    }
    return render(request, 'potholes/user_profile.html', context)


def report_pothole(request):
    """Report pothole view."""
    if request.method == 'POST':
        form = PotholeReportForm(request.POST, request.FILES)
        if form.is_valid():
            pothole = form.save(commit=False)
            if request.user.is_authenticated:
                pothole.user = request.user
            pothole.save()
            
            # Update user total reports (only if logged in)
            if request.user.is_authenticated:
                profile = request.user.profile
                profile.total_reports += 1
                profile.save()
            
            messages.success(request, 'Pothole reported successfully!')
            return redirect('community_feed')
    else:
        form = PotholeReportForm()
    
    context = {'form': form}
    return render(request, 'potholes/report_pothole.html', context)


def community_feed(request):
    """Community feed view showing all pothole reports."""
    potholes = Pothole.objects.all()
    
    # Filter by severity if provided
    severity_filter = request.GET.get('severity')
    if severity_filter:
        potholes = potholes.filter(severity=severity_filter)
    
    # Search functionality
    search_query = request.GET.get('search')
    if search_query:
        potholes = potholes.filter(
            Q(description__icontains=search_query) |
            Q(user__username__icontains=search_query)
        )
    
    # Order by votes if requested
    order_by = request.GET.get('order', 'recent')
    if order_by == 'votes':
        potholes = potholes.order_by('-vote_count')
    else:
        potholes = potholes.order_by('-created_at')
    
    # Annotate if user has voted and user truth score
    potholes = potholes.select_related('user__profile')
    
    if request.user.is_authenticated:
        user_votes = Vote.objects.filter(pothole=OuterRef('pk'), user=request.user)
        potholes = potholes.annotate(user_has_voted=Exists(user_votes))


    
    context = {
        'potholes': potholes,
        'order_by': order_by,
        'severity_filter': severity_filter,
        'search_query': search_query,
    }
    return render(request, 'potholes/community_feed.html', context)


@login_required
@require_POST
def upvote_pothole(request, pothole_id):
    """Upvote a pothole."""
    pothole = get_object_or_404(Pothole, id=pothole_id)
    user = request.user
    
    # Check if already voted
    vote = Vote.objects.filter(user=user, pothole=pothole).first()
    
    if vote:
        # Remove vote
        vote.delete()
        # Recalculate accurately
        pothole.vote_count = pothole.votes.count()
        voted = False
    else:
        # Add vote
        Vote.objects.get_or_create(user=user, pothole=pothole)
        # Recalculate accurately
        pothole.vote_count = pothole.votes.count()
        voted = True
    
    pothole.save()
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'voted': voted,
            'vote_count': pothole.vote_count
        })
    
    return redirect(request.META.get('HTTP_REFERER', 'community_feed'))

def get_pothole_stats(request):
    """API endpoint for fetching live vote counts and other stats."""
    pothole_ids = request.GET.getlist('ids[]')
    if not pothole_ids:
        return JsonResponse({'error': 'No IDs provided'}, status=400)
    
    stats = {}
    potholes = Pothole.objects.filter(id__in=pothole_ids)
    for p in potholes:
        stats[p.id] = {
            'vote_count': p.vote_count
        }
    
    return JsonResponse({'stats': stats})


def potholes_api(request):
    """API endpoint to fetch potholes as JSON for map."""
    potholes = Pothole.objects.values('id', 'latitude', 'longitude', 'severity', 'image', 'description', 'status')
    return JsonResponse(list(potholes), safe=False)


def map_view(request):
    """Map view for displaying potholes."""
    return render(request, 'potholes/map.html')


@login_required
def notifications(request):
    """User notifications view."""
    user_notifications = request.user.notifications.all().order_by('-created_at')
    
    context = {
        'notifications': user_notifications,
    }
    return render(request, 'potholes/notifications.html', context)


@login_required
def mark_notification_as_read(request, notification_id):
    """Mark notification as read."""
    notification = get_object_or_404(Notification, id=notification_id, user=request.user)
    notification.is_read = True
    notification.save()
    return redirect('notifications')


# ============== ADMIN VIEWS ==============

@login_required
def admin_required(view_func):
    """Decorator to check if user is admin/staff."""
    def wrapper(request, *args, **kwargs):
        if not request.user.is_staff:
            messages.error(request, 'You do not have permission to access this page.')
            return redirect('home')
        return view_func(request, *args, **kwargs)
    return wrapper


@login_required
def admin_dashboard(request):
    """Admin dashboard showing all pothole reports."""
    if not request.user.is_staff:
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('home')
    
    potholes = Pothole.objects.all().order_by('-created_at')
    
    # Filter by status
    status_filter = request.GET.get('status')
    if status_filter:
        potholes = potholes.filter(status=status_filter)
    
    # Filter by severity
    severity_filter = request.GET.get('severity')
    if severity_filter:
        potholes = potholes.filter(severity=severity_filter)
    
    # Statistics
    total_potholes = Pothole.objects.count()
    pending = Pothole.objects.filter(status='Pending').count()
    in_progress = Pothole.objects.filter(status='In Progress').count()
    fixed = Pothole.objects.filter(status='Fixed').count()
    invalid = Pothole.objects.filter(status='Invalid').count()
    
    context = {
        'potholes': potholes,
        'status_filter': status_filter,
        'severity_filter': severity_filter,
        'total': total_potholes,
        'pending': pending,
        'in_progress': in_progress,
        'fixed': fixed,
        'invalid': invalid,
    }
    return render(request, 'potholes/admin_dashboard.html', context)


@login_required
def update_pothole_status(request, pothole_id):
    """Update pothole status (admin only)."""
    if not request.user.is_staff:
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('home')
    
    pothole = get_object_or_404(Pothole, id=pothole_id)
    old_status = pothole.status
    
    if request.method == 'POST':
        form = PotholeUpdateForm(request.POST, request.FILES, instance=pothole)
        if form.is_valid():
            pothole = form.save()
            
            # Create notification for reporter (only if not anonymous)
            reporter = pothole.user
            if reporter:
                status_message = f"Your pothole report has been marked as '{pothole.status}'."
                Notification.objects.create(
                    user=reporter,
                    pothole=pothole,
                    notification_type=pothole.status.lower().replace(' ', '_'),
                    message=status_message
                )
            
            messages.success(request, 'Pothole updated successfully!')
            return redirect('admin_dashboard')
    else:
        form = PotholeUpdateForm(instance=pothole)
    
    context = {
        'form': form,
        'pothole': pothole,
    }
    return render(request, 'potholes/update_pothole.html', context)


def pothole_detail(request, pothole_id):
    """Detailed view of a single pothole."""
    pothole = get_object_or_404(Pothole, id=pothole_id)
    user_has_voted = False
    
    if request.user.is_authenticated:
        user_has_voted = Vote.objects.filter(user=request.user, pothole=pothole).exists()
    
    context = {
        'pothole': pothole,
        'user_has_voted': user_has_voted,
    }
    return render(request, 'potholes/pothole_detail.html', context)
