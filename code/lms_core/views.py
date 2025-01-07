from django.shortcuts import render, HttpResponse, get_object_or_404, redirect
from django.http import JsonResponse
from lms_core.models import Course, Comment, CourseContent, CourseMember, Announcement, Category
from django.core import serializers
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
import json
from django.utils import timezone
from django.contrib.auth import authenticate, login
from django.db.models import Count
from django import forms 
from django.utils.decorators import method_decorator
from django.views import View
from django.contrib import messages  
import logging

logger = logging.getLogger(__name__)

def index(request):
    return HttpResponse("<h1>Hello World</h1>")

def testing(request):
    dataCourse = Course.objects.all()
    dataCourse = serializers.serialize("python", dataCourse)
    return JsonResponse(dataCourse, safe=False)

def addData(request): 
    course = Course(
        name = "Belajar Django",
        description = "Belajar Django",
        price = 2000000,
        teacher = User.objects.get(username="udin")
    )
    course.save()
    return JsonResponse({"message": "Data berhasil ditambahkan"})

def editData(request):
    course = Course.objects.filter(name="Belajar Django").first()
    course.name = "Belajar Django Setelah update"
    course.save()
    return JsonResponse({"message": "Data berhasil diubah"})

def deleteData(request):
    course = Course.objects.filter(name__icontains="Belajar Django").first()
    course.delete()
    return JsonResponse({"message": "Data berhasil dihapus"})

@method_decorator(csrf_exempt, name='dispatch')
class RegisterView(View):
    def post(self, request):
        data = json.loads(request.body)
        username = data.get('username')
        password = data.get('password')
        email = data.get('email')

        if User.objects.filter(username=username).exists():
            return JsonResponse({"error": "Username already exists"}, status=400)

        user = User.objects.create_user(username=username, password=password, email=email)
        return JsonResponse({"message": "User registered successfully"}, status=201)

register = RegisterView.as_view()

@csrf_exempt
def register_user(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        username = data.get('username')
        password = data.get('password')
        email = data.get('email')
        first_name = data.get('first_name')
        last_name = data.get('last_name')

        if User.objects.filter(username=username).exists():
            return JsonResponse({"error": "Username sudah ada"}, status=400)

        user = User.objects.create_user(username=username, password=password, email=email, first_name=first_name, last_name=last_name)
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            return JsonResponse({"message": "Pengguna berhasil didaftarkan dan masuk"}, status=201)
        else:
            return JsonResponse({"error": "Autentikasi gagal"}, status=400)

    return JsonResponse({"error": "Metode permintaan tidak valid"}, status=405)

@csrf_exempt
def enroll_course(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        course_id = data.get('course_id')
        user_id = data.get('user_id')

        try:
            course = Course.objects.get(id=course_id)
            user = User.objects.get(id=user_id)

            if CourseMember.objects.filter(course_id=course, user_id=user).exists():
                return JsonResponse({"error": "User sudah terdaftar di course ini"}, status=400)

            enrolled_students_count = CourseMember.objects.filter(course_id=course).count()
            if enrolled_students_count >= course.max_students:
                return JsonResponse({"error": "Kuota course sudah penuh"}, status=400)

            CourseMember.objects.create(course_id=course, user_id=user)
            return JsonResponse({"message": "User berhasil didaftarkan ke course"}, status=201)

        except Course.DoesNotExist:
            return JsonResponse({"error": "Course tidak ditemukan"}, status=404)
        except User.DoesNotExist:
            return JsonResponse({"error": "User tidak ditemukan"}, status=404)

    return JsonResponse({"error": "Metode permintaan tidak valid"}, status=405)

def list_comments(request, content_id):
    comments = Comment.objects.filter(content_id=content_id, is_approved=True)
    data = serializers.serialize("json", comments)
    return JsonResponse(data, safe=False)

def user_activity_dashboard(request, user_id):
    try:
        user = User.objects.get(id=user_id)
        stats = {
            'courses_as_student': CourseMember.objects.filter(user_id=user, roles='std').count(),
            'courses_created': Course.objects.filter(teacher=user).count(),
            'comments_written': Comment.objects.filter(member_id__user_id=user).count(),
            'contents_completed': CourseMember.objects.filter(user_id=user, is_completed=True).count()  
        }
        return JsonResponse(stats, status=200)
    except User.DoesNotExist:
        return JsonResponse({"error": "User tidak ditemukan"}, status=404)

def course_analytics(request, course_id):
    try:
        course = Course.objects.get(id=course_id)
        stats = {
            'members_count': CourseMember.objects.filter(course_id=course).count(),
            'contents_count': CourseContent.objects.filter(course_id=course).count(),
            'comments_count': Comment.objects.filter(content_id__course_id=course).count(),
        }
        return JsonResponse(stats, status=200)
    except Course.DoesNotExist:
        return JsonResponse({"error": "Course tidak ditemukan"}, status=404)

def list_course_contents(request, course_id):
    contents = CourseContent.objects.filter(course_id=course_id, release_date__lte=timezone.now())
    data = serializers.serialize("json", contents)
    return JsonResponse(data, safe=False)

class BatchEnrollForm(forms.Form):
    course = forms.ModelChoiceField(queryset=Course.objects.all(), label="Course")
    students = forms.ModelMultipleChoiceField(queryset=User.objects.filter(is_staff=False), label="Students")

def batch_enroll(request):
    if request.method == 'POST':
        form = BatchEnrollForm(request.POST)
        if form.is_valid():
            course = form.cleaned_data['course']
            students = form.cleaned_data['students']
            if CourseMember.objects.filter(course_id=course).count() + len(students) > course.max_students:
                messages.error(request, "Not enough slots available for all students")
                return redirect('batch_enroll')
            for student in students:
                if not CourseMember.objects.filter(course_id=course, user_id=student).exists():
                    CourseMember.objects.create(course_id=course, user_id=student)
            messages.success(request, "Students enrolled successfully")
            return redirect('admin:index')
    else:
        form = BatchEnrollForm()
    return render(request, 'admin/batch_enroll.html', {'form': form})

@csrf_exempt
def mark_course_complete(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        course_id = data.get('course_id')
        user_id = data.get('user_id')

        try:
            course_member = CourseMember.objects.get(course_id=course_id, user_id=user_id)
            course_member.is_completed = True
            course_member.save()
            return JsonResponse({"message": "Course marked as complete"}, status=200)
        except CourseMember.DoesNotExist:
            return JsonResponse({"error": "CourseMember tidak ditemukan"}, status=404)

    return JsonResponse({"error": "Metode permintaan tidak valid"}, status=405)

@csrf_exempt
def check_course_completion(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        course_id = data.get('course_id')
        user_id = data.get('user_id')

        try:
            course_member = CourseMember.objects.get(course_id=course_id, user_id=user_id)
            return JsonResponse({"is_completed": course_member.is_completed}, status=200)
        except CourseMember.DoesNotExist:
            return JsonResponse({"error": "CourseMember tidak ditemukan"}, status=404)

    return JsonResponse({"error": "Metode permintaan tidak valid"}, status=405)

def certificate(request, course_id, user_id):
    course = get_object_or_404(Course, id=course_id)
    user = get_object_or_404(User, id=user_id)
    course_member = get_object_or_404(CourseMember, course_id=course, user_id=user)

    if not course_member.is_completed:
        return HttpResponse("User belum menyelesaikan kursus ini", status=403)

    context = {
        'course': course,
        'user': user,
        'date': timezone.now()
    }
    return render(request, 'certificate.html', context)

@csrf_exempt
def create_announcement(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        course_id = data.get('course_id')
        title = data.get('title')
        content = data.get('content')
        release_date = data.get('release_date')
        user_id = data.get('user_id')

        try:
            course = Course.objects.get(id=course_id)
            user = User.objects.get(id=user_id)

            if course.teacher != user:
                return JsonResponse({"error": "Hanya teacher yang dapat membuat pengumuman"}, status=403)

            announcement = Announcement.objects.create(
                course=course,
                title=title,
                content=content,
                release_date=release_date
            )
            return JsonResponse({"message": "Pengumuman berhasil dibuat"}, status=201)

        except Course.DoesNotExist:
            return JsonResponse({"error": "Course tidak ditemukan"}, status=404)
        except User.DoesNotExist:
            return JsonResponse({"error": "User tidak ditemukan"}, status=404)

    return JsonResponse({"error": "Metode permintaan tidak valid"}, status=405)

def show_announcements(request, course_id):
    try:
        course = Course.objects.get(id=course_id)
        announcements = Announcement.objects.filter(course=course, release_date__lte=timezone.now())
        data = serializers.serialize("json", announcements)
        return JsonResponse(data, safe=False)
    except Course.DoesNotExist:
        return JsonResponse({"error": "Course tidak ditemukan"}, status=404)

@csrf_exempt
def edit_announcement(request, announcement_id):
    if request.method == 'POST':
        data = json.loads(request.body)
        title = data.get('title')
        content = data.get('content')
        release_date = data.get('release_date')
        user_id = data.get('user_id')

        try:
            announcement = Announcement.objects.get(id=announcement_id)
            user = User.objects.get(id=user_id)

            if announcement.course.teacher != user:
                return JsonResponse({"error": "Hanya teacher yang dapat mengedit pengumuman"}, status=403)

            announcement.title = title
            announcement.content = content
            announcement.release_date = release_date
            announcement.save()
            return JsonResponse({"message": "Pengumuman berhasil diubah"}, status=200)

        except Announcement.DoesNotExist:
            return JsonResponse({"error": "Pengumuman tidak ditemukan"}, status=404)
        except User.DoesNotExist:
            return JsonResponse({"error": "User tidak ditemukan"}, status=404)

    return JsonResponse({"error": "Metode permintaan tidak valid"}, status=405)

@csrf_exempt
def delete_announcement(request, announcement_id):
    if request.method == 'POST':
        data = json.loads(request.body)
        user_id = data.get('user_id')

        try:
            announcement = Announcement.objects.get(id=announcement_id)
            user = User.objects.get(id=user_id)

            if announcement.course.teacher != user:
                return JsonResponse({"error": "Hanya teacher yang dapat menghapus pengumuman"}, status=403)

            announcement.delete()
            return JsonResponse({"message": "Pengumuman berhasil dihapus"}, status=200)

        except Announcement.DoesNotExist:
            return JsonResponse({"error": "Pengumuman tidak ditemukan"}, status=404)
        except User.DoesNotExist:
            return JsonResponse({"error": "User tidak ditemukan"}, status=404)

    return JsonResponse({"error": "Metode permintaan tidak valid"}, status=405)

@csrf_exempt
def add_category(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        name = data.get('name')
        user_id = data.get('user_id')

        try:
            user = User.objects.get(id=user_id)
            category = Category.objects.create(name=name, created_by=user)
            return JsonResponse({"message": "Kategori berhasil dibuat"}, status=201)
        except User.DoesNotExist:
            return JsonResponse({"error": "User tidak ditemukan"}, status=404)

    return JsonResponse({"error": "Metode permintaan tidak valid"}, status=405)

def show_categories(request):
    categories = Category.objects.all()
    data = serializers.serialize("json", categories)
    return JsonResponse(data, safe=False)

@csrf_exempt
def delete_category(request, category_id):
    if request.method == 'POST':
        data = json.loads(request.body)
        user_id = data.get('user_id')

        try:
            category = Category.objects.get(id=category_id)
            user = User.objects.get(id=user_id)

            if category.created_by != user:
                return JsonResponse({"error": "Hanya user yang membuat kategori yang dapat menghapusnya"}, status=403)

            category.delete()
            return JsonResponse({"message": "Kategori berhasil dihapus"}, status=200)

        except Category.DoesNotExist:
            return JsonResponse({"error": "Kategori tidak ditemukan"}, status=404)
        except User.DoesNotExist:
            return JsonResponse({"error": "User tidak ditemukan"}, status=404)

    return JsonResponse({"error": "Metode permintaan tidak valid"}, status=405)

@csrf_exempt
def api_batch_enroll(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        course_id = data.get('course_id')
        student_ids = data.get('student_ids')

        try:
            course = Course.objects.get(id=course_id)
            if CourseMember.objects.filter(course_id=course).count() + len(student_ids) > course.max_students:
                return JsonResponse({"error": "Not enough slots available for all students"}, status=400)

            for student_id in student_ids:
                student = User.objects.get(id=student_id)
                if not CourseMember.objects.filter(course_id=course, user_id=student).exists():
                    CourseMember.objects.create(course_id=course, user_id=student)

            return JsonResponse({"message": "Students enrolled successfully"}, status=201)

        except Course.DoesNotExist:
            return JsonResponse({"error": "Course not found"}, status=404)
        except User.DoesNotExist:
            return JsonResponse({"error": "One or more users not found"}, status=404)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Invalid request method"}, status=405)

@csrf_exempt
def moderate_comment(request, comment_id):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            is_approved = data.get('is_approved')
            user_id = data.get('user_id')

            comment = Comment.objects.get(id=comment_id)
            user = User.objects.get(id=user_id)

            if comment.content_id.course_id.teacher != user:
                return JsonResponse({"error": "Hanya teacher yang dapat memoderasi komentar"}, status=403)

            comment.is_approved = is_approved
            comment.save()
            return JsonResponse({"message": "Komentar berhasil dimoderasi"}, status=200)

        except Comment.DoesNotExist:
            logger.error("Comment not found", exc_info=True)
            return JsonResponse({"error": "Komentar tidak ditemukan"}, status=404)
        except User.DoesNotExist:
            logger.error("User not found", exc_info=True)
            return JsonResponse({"error": "User tidak ditemukan"}, status=404)
        except Exception as e:
            logger.error("An unexpected error occurred", exc_info=True)
            return JsonResponse({"error": "An unexpected error occurred"}, status=500)

    return JsonResponse({"error": "Metode permintaan tidak valid"}, status=405)

@csrf_exempt
def set_max_students(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        course_id = data.get('course_id')
        max_students = data.get('max_students')

        try:
            course = Course.objects.get(id=course_id)
            course.max_students = max_students
            course.save()
            return JsonResponse({"message": "Jumlah maksimal siswa berhasil ditetapkan"}, status=200)
        except Course.DoesNotExist:
            return JsonResponse({"error": "Course tidak ditemukan"}, status=404)

    return JsonResponse({"error": "Metode permintaan tidak valid"}, status=405)