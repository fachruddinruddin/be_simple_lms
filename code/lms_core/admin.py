from django import forms
from django.contrib import admin
from django.urls import path
from django.shortcuts import render, redirect
from django.contrib import messages
from lms_core.models import Course, CourseMember, CourseContent, Comment, Announcement, Category 
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import UserCreationForm, UserChangeForm

class BatchEnrollForm(forms.Form):
    course = forms.ModelChoiceField(queryset=Course.objects.all(), label="Course")
    students = forms.ModelMultipleChoiceField(queryset=User.objects.filter(is_staff=False), label="Students")

def batch_enroll(request):
    if request.method == 'POST':
        form = BatchEnrollForm(request.POST)
        if form.is_valid():
            course = form.cleaned_data['course']
            students = form.cleaned_data['students']
            for student in students:
                CourseMember.objects.get_or_create(course_id=course, user_id=student)
            messages.success(request, "Students enrolled successfully")
            return redirect('admin:index')
    else:
        form = BatchEnrollForm()
    return render(request, 'admin/batch_enroll.html', {'form': form})

class MyAdminSite(admin.AdminSite):
    site_header = 'LMS Administration'

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('batch_enroll/', self.admin_view(batch_enroll), name='batch_enroll'),
        ]
        return custom_urls + urls

admin_site = MyAdminSite(name='myadmin')

@admin.register(Course, site=admin_site)
class CourseAdmin(admin.ModelAdmin):
    list_display = ["name", "price", "description", "teacher", 'created_at']
    list_filter = ["teacher"]
    search_fields = ["name", "description"]
    readonly_fields = ["created_at", "updated_at"]
    fields = ["name", "description", "price", "image", "teacher", "max_students", "created_at", "updated_at"]

@admin.register(CourseMember, site=admin_site)
class CourseMemberAdmin(admin.ModelAdmin):
    list_display = ["course_id", "user_id", "roles", "created_at"]
    list_filter = ["course_id", "user_id", "roles"]
    search_fields = ["course_id_name", "user_id_username"]
    readonly_fields = ["created_at", "updated_at"]
    fields = ["course_id", "user_id", "roles", "created_at", "updated_at"]

@admin.register(CourseContent, site=admin_site)
class CourseContentAdmin(admin.ModelAdmin):
    list_display = ["name", "course_id", "release_date", "created_at"]
    list_filter = ["course_id"]
    search_fields = ["name", "course_id__name"]
    readonly_fields = ["created_at", "updated_at"]
    fields = ["name", "description", "file_attachment", "course_id", "parent_id", "release_date", "created_at", "updated_at"]

@admin.register(Comment, site=admin_site)
class CommentAdmin(admin.ModelAdmin):
    list_display = ["content_id", "member_id", "comment", "is_approved", "created_at"]
    list_filter = ["content_id", "member_id", "is_approved"]
    search_fields = ["comment", "member_id_user_id_username"]
    readonly_fields = ["created_at", "updated_at"]
    fields = ["content_id", "member_id", "comment", "is_approved", "created_at", "updated_at"]

@admin.register(Announcement, site=admin_site)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ["title", "course", "release_date", "created_at"]
    list_filter = ["course", "release_date"]
    search_fields = ["title", "course__name"]
    readonly_fields = ["created_at", "updated_at"]
    fields = ["course", "title", "content", "release_date", "created_at", "updated_at"]

@admin.register(Category, site=admin_site)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "created_by", "created_at"]
    search_fields = ["name", "created_by__username"]
    readonly_fields = ["created_at", "updated_at"]
    fields = ["name", "created_by", "created_at", "updated_at"]

class CustomUserAdmin(BaseUserAdmin):
    add_form = UserCreationForm
    form = UserChangeForm
    model = User
    list_display = ['username', 'email', 'first_name', 'last_name', 'is_staff']
    list_filter = ['is_staff', 'is_superuser', 'is_active']
    search_fields = ['username', 'email', 'first_name', 'last_name']
    ordering = ['username']
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2', 'email', 'first_name', 'last_name', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
    )

admin_site.register(User, CustomUserAdmin)