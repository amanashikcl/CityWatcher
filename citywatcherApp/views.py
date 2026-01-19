from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from .models import UserProfile, Report
import folium
from folium import plugins


from django.db import IntegrityError # Add this import at the top

def register(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user_type = request.POST.get('user_type')

        if not username or not password:
            messages.error(request, 'Username and password are required.')
            return render(request, 'register.html')


        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username is already taken. Please choose another.')
            return render(request, 'register.html')

        try:
            user = User.objects.create_user(username=username, password=password)
            UserProfile.objects.create(user=user, user_type=user_type)
            
            messages.success(request, 'Registration successful! Please log in.')
            return redirect('login')
            
        except IntegrityError:
            messages.error(request, 'A database error occurred. Please try again.')
            return render(request, 'register.html')

    return render(request, 'register.html')


def user_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid credentials')

    return render(request, 'login.html')


def user_logout(request):
    logout(request)
    return redirect('login')


@login_required
def dashboard(request):
    try:
        profile = UserProfile.objects.get(user=request.user)
    except UserProfile.DoesNotExist:
        # Create admin profile for superusers without a profile
        if request.user.is_superuser:
            profile = UserProfile.objects.create(user=request.user, user_type='admin')
        else:
            messages.error(request, 'User profile not found. Please contact admin.')
            return redirect('login')

    if profile.user_type == 'citizen':
        reports = Report.objects.filter(citizen=request.user)
        return render(request, 'citizen_dashboard.html', {'reports': reports})

    elif profile.user_type == 'worker':
        reports = Report.objects.filter(worker=request.user)
        return render(request, 'worker_dashboard.html', {'reports': reports})

    elif profile.user_type == 'admin':
        reports = Report.objects.all()
        workers = User.objects.filter(userprofile__user_type='worker')

        #map
        m = folium.Map(location=[10.0, 76.0], zoom_start=10)

        for report in reports:
            color = 'red' if report.status == 'pending' else 'orange' if report.status == 'assigned' else 'green'
            popup_html = f"""
                <b>{report.title}</b><br>
                Status: {report.status}<br>
                <a href='/report/{report.id}/' target='_blank'>View Details</a>
            """
            folium.Marker(
                [report.latitude, report.longitude],
                popup=folium.Popup(popup_html, max_width=200),
                icon=folium.Icon(color=color)
            ).add_to(m)

        map_html = m._repr_html_()
        return render(request, 'admin_dashboard.html', {
            'reports': reports,
            'workers': workers,
            'map_html': map_html
        })

    return redirect('login')


@login_required
def create_report(request):
    if request.method == 'POST':
        title = request.POST['title']
        description = request.POST['description']
        image = request.FILES['image']
        latitude = float(request.POST['latitude'])
        longitude = float(request.POST['longitude'])

        Report.objects.create(
            title=title,
            description=description,
            image=image,
            latitude=latitude,
            longitude=longitude,
            citizen=request.user
        )
        messages.success(request, 'Report submitted successfully!')
        return redirect('dashboard')

    return render(request, 'create_report.html')


@login_required
def report_detail(request, report_id):
    report = get_object_or_404(Report, id=report_id)
    profile = UserProfile.objects.get(user=request.user)

    return render(request, 'report_detail.html', {
        'report': report,
        'user_type': profile.user_type
    })


@login_required
def assign_worker(request, report_id):
    if request.method == 'POST':
        report = get_object_or_404(Report, id=report_id)
        worker_id = request.POST['worker_id']
        worker = User.objects.get(id=worker_id)

        report.worker = worker
        report.status = 'assigned'
        report.save()
        messages.success(request, 'Worker assigned successfully!')

    return redirect('dashboard')


@login_required
def complete_report(request, report_id):
    report = get_object_or_404(Report, id=report_id)
    report.status = 'completed'
    report.save()
    messages.success(request, 'Report marked as completed!')
    return redirect('dashboard')


@login_required
def delete_report(request, report_id):
    report = get_object_or_404(Report, id=report_id)
    profile = UserProfile.objects.get(user=request.user)
    
    # Only admins can delete reports
    if profile.user_type == 'admin':
        report.delete()
        messages.success(request, 'Report deleted successfully!')
    else:
        messages.error(request, 'You do not have permission to delete reports.')
    
    return redirect('dashboard')