"""
URL configuration for simplelms project.

The urlpatterns list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
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
from django.urls import path, include
from lms_core.views import index, testing, addData, editData, deleteData, register, list_comments, user_activity_dashboard, course_analytics, list_course_contents, register_user, enroll_course, batch_enroll  # Import the new view
from lms_core.api import apiv1  
from lms_core.admin import admin_site  # Import admin_site yang baru

urlpatterns = [
    path('api/v1/', apiv1.urls),
    path('admin/', admin_site.urls),  # Gunakan admin_site yang baru
    path('testing/', testing),
    path('tambah/', addData),
    path('ubah/', editData),
    path('hapus/', deleteData),
    path('register/', register, name='register'),
    path('register_user/', register_user, name='register_user'),  # Add new URL pattern
    path('comments/<int:content_id>/', list_comments, name='list_comments'),
    path('user_activity/<int:user_id>/', user_activity_dashboard, name='user_activity_dashboard'),
    path('course_analytics/<int:course_id>/', course_analytics, name='course_analytics'),
    path('course_contents/<int:course_id>/', list_course_contents, name='list_course_contents'),
    path('enroll_course/', enroll_course, name='enroll_course'),  # Add new URL pattern
    path('batch_enroll/', batch_enroll, name='batch_enroll'),  # Add new URL pattern
    path('', index),
]