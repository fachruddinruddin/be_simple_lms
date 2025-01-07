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
from lms_core.views import index, testing, addData, editData, deleteData, register, list_comments, user_activity_dashboard, course_analytics, list_course_contents, register_user, enroll_course, batch_enroll, mark_course_complete, check_course_completion, certificate, create_announcement, show_announcements, edit_announcement, delete_announcement, add_category, show_categories, delete_category, api_batch_enroll, moderate_comment, set_max_students  
from lms_core.api import apiv1 
from lms_core.admin import admin_site 

urlpatterns = [
    path('api/v1/', apiv1.urls), 
    path('admin/', admin_site.urls), 
    path('testing/', testing),
    path('tambah/', addData),
    path('ubah/', editData),
    path('hapus/', deleteData),
    path('register/', register, name='register'),
    path('register_user/', register_user, name='register_user'),  
    path('comments/<int:content_id>/', list_comments, name='list_comments'),
    path('user_activity/<int:user_id>/', user_activity_dashboard, name='user_activity_dashboard'),
    path('course_analytics/<int:course_id>/', course_analytics, name='course_analytics'),
    path('course_contents/<int:course_id>/', list_course_contents, name='list_course_contents'),
    path('enroll_course/', enroll_course, name='enroll_course'),  
    path('batch_enroll/', batch_enroll, name='batch_enroll'),  
    path('mark_course_complete/', mark_course_complete, name='mark_course_complete'),  
    path('check_course_completion/', check_course_completion, name='check_course_completion'),  
    path('certificate/<int:course_id>/<int:user_id>/', certificate, name='certificate'),  
    path('create_announcement/', create_announcement, name='create_announcement'),  
    path('show_announcements/<int:course_id>/', show_announcements, name='show_announcements'),  
    path('edit_announcement/<int:announcement_id>/', edit_announcement, name='edit_announcement'),  
    path('delete_announcement/<int:announcement_id>/', delete_announcement, name='delete_announcement'),  
    path('add_category/', add_category, name='add_category'),  
    path('show_categories/', show_categories, name='show_categories'),  
    path('delete_category/<int:category_id>/', delete_category, name='delete_category'),  
    path('api/batch_enroll/', api_batch_enroll, name='api_batch_enroll'),  
    path('moderate_comment/<int:comment_id>/', moderate_comment, name='moderate_comment'),  
    path('set_max_students/', set_max_students, name='set_max_students'),  
    path('', index),
]