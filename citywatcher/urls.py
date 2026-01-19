"""
URL configuration for citywatcher project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from citywatcherApp import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.user_login, name='home'),
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('report/create/', views.create_report, name='create_report'),
    path('report/<int:report_id>/', views.report_detail, name='report_detail'),
    path('report/<int:report_id>/assign/', views.assign_worker, name='assign_worker'),
    path('report/<int:report_id>/complete/', views.complete_report, name='complete_report'),
    path('report/<int:report_id>/delete/', views.delete_report, name='delete_report'),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)