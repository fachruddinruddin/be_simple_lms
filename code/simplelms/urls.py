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
from lms_core.views import index, testing, addData, editData, deleteData, register, list_comments, user_activity_dashboard, course_analytics, list_course_contents, register_user, enroll_course, batch_enroll, mark_course_complete, check_course_completion, certificate, create_announcement, show_announcements, edit_announcement, delete_announcement, add_category, show_categories, delete_category, api_batch_enroll, moderate_comment  # Import the new views
from lms_core.api import apiv1  # Import the API
from lms_core.admin import admin_site  # Import admin_site yang baru

urlpatterns = [
    path('api/v1/', apiv1.urls),  # Add the API URL pattern
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
    path('mark_course_complete/', mark_course_complete, name='mark_course_complete'),  # Add new URL pattern
    path('check_course_completion/', check_course_completion, name='check_course_completion'),  # Add new URL pattern
    path('certificate/<int:course_id>/<int:user_id>/', certificate, name='certificate'),  # Add new URL pattern
    path('create_announcement/', create_announcement, name='create_announcement'),  # Add new URL pattern
    path('show_announcements/<int:course_id>/', show_announcements, name='show_announcements'),  # Add new URL pattern
    path('edit_announcement/<int:announcement_id>/', edit_announcement, name='edit_announcement'),  # Add new URL pattern
    path('delete_announcement/<int:announcement_id>/', delete_announcement, name='delete_announcement'),  # Add new URL pattern
    path('add_category/', add_category, name='add_category'),  # Add new URL pattern
    path('show_categories/', show_categories, name='show_categories'),  # Add new URL pattern
    path('delete_category/<int:category_id>/', delete_category, name='delete_category'),  # Add new URL pattern
    path('api/batch_enroll/', api_batch_enroll, name='api_batch_enroll'),  # Add new URL pattern
    path('moderate_comment/<int:comment_id>/', moderate_comment, name='moderate_comment'),  # Ensure this URL pattern is correct
    path('', index),
]