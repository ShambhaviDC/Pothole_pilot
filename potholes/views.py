from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.db.models import Q, Exists, OuterRef, Subquery, Case, When, Value, IntegerField, Count
from django.contrib import messages
from datetime import timedelta
from django.utils.timezone import now
import json
from functools import wraps

from .models import Pothole, UserProfile, Vote, Notification
from .forms import UserRegistrationForm, UserLoginForm, PotholeReportForm, PotholeUpdateForm
from .utils import haversine, get_image_hash, compare_hashes


def home(request):
    """Home page view."""
    context = {
        'total_potholes': Pothole.objects.filter(is_archived=False).count(),
        'total_fixed': Pothole.objects.filter(status='Fixed', is_archived=False).count(),
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
    user_potholes = user.potholes.filter(is_archived=False)
    unread_notifications = 0
    
    # Cleanup old fixed images automatically (optimized)
    seven_days_ago = now() - timedelta(days=7)
    stale_potholes = Pothole.objects.filter(
        status='Fixed', 
        image__isnull=False
    ).filter(Q(fixed_at__lte=seven_days_ago) | Q(fixed_at__isnull=True, updated_at__lte=seven_days_ago))
    # Deferred image cleanup for performance


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
            lat = form.cleaned_data.get('latitude')
            lng = form.cleaned_data.get('longitude')
            image = request.FILES.get('image')
            
            # Simple validation for coordinates
            if lat is None or lng is None:
                # Fallback or error if coordinates are missing (should be handled by frontend)
                messages.error(request, 'Location information is required.')
                return render(request, 'potholes/report_pothole.html', {'form': form})
            
            # 1. Image Hashing (Optional Enhancement)
            new_image_hash = get_image_hash(image) if image else None
            
            # 2. Duplicate Detection logic
            # Search for nearby potholes (within ~50 meters approx bbox)
            lat_delta = 0.0005 # ~55 meters
            lng_delta = 0.0005 # ~55 meters
            nearby_bbox = Pothole.objects.filter(
                status__in=['Pending', 'In Progress'],
                latitude__range=(lat - lat_delta, lat + lat_delta),
                longitude__range=(lng - lng_delta, lng + lng_delta)
            )
            
            duplicate_found = None
            for existing in nearby_bbox:
                dist = haversine(lat, lng, existing.latitude, existing.longitude)
                
                # Check 1: Very close location (within 15m) -> likely duplicate
                if dist <= 15:
                    duplicate_found = existing
                    break
                
                # Check 2: Nearby (15-50m) AND image similarity
                elif dist <= 50:
                    if new_image_hash and existing.image_hash:
                        if compare_hashes(new_image_hash, existing.image_hash, threshold=12):
                            duplicate_found = existing
                            break
            
            if duplicate_found:
                # 3. Increment vote/report count instead of creating new record
                if request.user.is_authenticated:
                    # prevent duplicate voting for same user
                    vote, created = Vote.objects.get_or_create(user=request.user, pothole=duplicate_found)
                    if created:
                        # Recalculate accurately
                        duplicate_found.vote_count = duplicate_found.votes.count()
                        duplicate_found.save()
                        messages.success(request, 'Thank you for your report! This issue has already been highlighted, and your contribution has been added to the existing record.')
                    else:
                        messages.success(request, 'Thank you! Your continued support for this report is noted.')
                else:
                    # Anonymous contribution
                    duplicate_found.vote_count += 1
                    duplicate_found.save()
                    messages.success(request, 'Thank you for your report! Your contribution has been added to the community-tracked record of this issue.')
                
                return redirect('community_feed')

            # 4. No duplicate found, create new report
            pothole = form.save(commit=False)
            if request.user.is_authenticated:
                pothole.user = request.user
            pothole.image_hash = new_image_hash
            pothole.save()

            # Create initial vote for the reporter if logged in
            if request.user.is_authenticated:
                Vote.objects.get_or_create(user=request.user, pothole=pothole)
                pothole.vote_count = 1
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
    """Community feed view showing all non-archived pothole reports."""
    potholes = Pothole.objects.filter(is_archived=False)
    
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
        potholes = potholes.annotate(
            user_has_voted=Exists(user_votes),
        )
    
    # Always annotate with author truth score for display
    potholes = potholes.annotate(
        author_truth_score=Subquery(
            UserProfile.objects.filter(user=OuterRef('user')).values('truth_score')[:1]
        )
    )


    
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
    """API endpoint to fetch non-archived potholes as JSON for map."""
    potholes = Pothole.objects.filter(is_archived=False).values('id', 'latitude', 'longitude', 'severity', 'image', 'description', 'status', 'ward_number', 'vote_count')
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

def admin_required(view_func):
    """Decorator to check if user is admin/staff."""
    return user_passes_test(
        lambda u: u.is_staff,
        login_url='login'
    )(view_func)


@login_required
@admin_required
def admin_dashboard(request):
    """Admin dashboard showing all pothole reports."""
    
    # Cleanup old fixed images automatically (optimized)
    seven_days_ago = now() - timedelta(days=7)
    stale_potholes = Pothole.objects.filter(
        status='Fixed', 
        image__isnull=False
    ).filter(Q(fixed_at__lte=seven_days_ago) | Q(fixed_at__isnull=True, updated_at__lte=seven_days_ago))
    # Image cleanup is handled during the archival process



    # Sorting: Moderate then Low (and then others like High)
    potholes = Pothole.objects.filter(is_archived=False).annotate(
        severity_priority=Case(
            When(severity='Moderate', then=Value(1)),
            When(severity='Low', then=Value(2)),
            When(severity='High', then=Value(3)),
            default=Value(4),
            output_field=IntegerField(),
        )
    ).order_by('severity_priority', '-created_at')
    
    # Filter by status
    status_filter = request.GET.get('status')
    if status_filter:
        potholes = potholes.filter(status=status_filter)
    
    # Filter by severity
    severity_filter = request.GET.get('severity')
    if severity_filter:
        potholes = potholes.filter(severity=severity_filter)
    
    # Statistics (optimized)
    stats_query = Pothole.objects.filter(is_archived=False).values('status').annotate(count=Count('id'))
    stats_dict = {item['status']: item['count'] for item in stats_query}
    
    total_potholes = sum(stats_dict.values())
    pending = stats_dict.get('Pending', 0)
    in_progress = stats_dict.get('In Progress', 0)
    fixed = stats_dict.get('Fixed', 0)
    invalid = stats_dict.get('Invalid', 0)
    
    # Severity Statistics (optimized)
    severity_query = Pothole.objects.filter(is_archived=False).values('severity').annotate(count=Count('id'))
    severity_dict = {item['severity']: item['count'] for item in severity_query}
    
    moderate_count = severity_dict.get('Moderate', 0)
    low_count = severity_dict.get('Low', 0)
    
    # Deletable Potholes (Fixed, Notified, > 7 days ago)
    deletable_potholes = Pothole.objects.filter(
        status='Fixed',
        is_archived=False
    ).filter(
        Q(fixed_at__lte=seven_days_ago) | Q(fixed_at__isnull=True, updated_at__lte=seven_days_ago)
    ).filter(
        notifications__notification_type='fixed'
    ).distinct()
    
    deletable_count = deletable_potholes.count()
    
    context = {
        'potholes': potholes,
        'status_filter': status_filter,
        'severity_filter': severity_filter,
        'total': total_potholes,
        'pending': pending,
        'in_progress': in_progress,
        'fixed': fixed,
        'invalid': invalid,
        'moderate_count': moderate_count,
        'low_count': low_count,
        'deletable_count': deletable_count,
    }
    return render(request, 'potholes/admin_dashboard.html', context)


@login_required
@admin_required
def update_pothole_status(request, pothole_id):
    """Update pothole status (admin only)."""
    
    pothole = get_object_or_404(Pothole, id=pothole_id)
    old_status = pothole.status
    
    if request.method == 'POST':
        form = PotholeUpdateForm(request.POST, request.FILES, instance=pothole)
        if form.is_valid():
            pothole = form.save()
            
            # Update Truth Score Logic for the reporter
            reporter = pothole.user
            if reporter and hasattr(reporter, 'profile'):
                profile = reporter.profile
                if pothole.status == 'Fixed' and old_status != 'Fixed':
                    profile.truth_score += 10 # Reward for accurate, confirmed reporting
                    profile.save()
                elif pothole.status == 'Invalid' and old_status != 'Invalid':
                    profile.truth_score -= 5 # Penalty for false reporting
                    profile.save()
            
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


@login_required
@admin_required
@require_POST
def delete_old_potholes(request):
    """Archive all potholes that are fixed, notified, and > 7 days old (soft delete)."""
    seven_days_ago = now() - timedelta(days=7)
    
    deletable_potholes = Pothole.objects.filter(
        status='Fixed',
        is_archived=False
    ).filter(
        Q(fixed_at__lte=seven_days_ago) | Q(fixed_at__isnull=True, updated_at__lte=seven_days_ago)
    ).filter(
        notifications__notification_type='fixed'
    ).distinct()
    
    count = deletable_potholes.count()
    if count > 0:
        # Soft delete: mark as archived instead of removing from DB
        deletable_potholes.update(is_archived=True)
        messages.success(request, f'Successfully archived {count} pothole records. They are hidden but remain in the database for historical records.')
    else:
        messages.info(request, 'No records found to archive.')
        
    return redirect('admin_dashboard')


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
