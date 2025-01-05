from django.shortcuts import render, HttpResponse
from django.http import JsonResponse
from lms_core.models import Course, Comment, CourseContent
from django.core import serializers
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
import json
from django.utils import timezone
from django.contrib.auth import authenticate, login
from django.db.models import Count
from django import forms  # Tambahkan impor ini

def index(request):
    return HttpResponse("<h1>Hello World</h1>")
    
def testing(request):
    dataCourse = Course.objects.all()
    dataCourse = serializers.serialize("python", dataCourse)
    return JsonResponse(dataCourse, safe=False)

def addData(request): 
    course = Course(
        name = "Belajar Django",
        description = "Belajar Django dengan Mudah",
        price = 1000000,
        teacher = User.objects.get(username="reza")
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

@csrf_exempt
def register(request):
    if request.method == 'POST':
        username = "udin"
        password = "udin123"
        email = "udin@gmail.com"

        if User.objects.filter(username=username).exists():
            return JsonResponse({"error": "Username already exists"}, status=400)

        User.objects.create_user(username=username, password=password, email=email)
        return JsonResponse({"message": "User registered successfully"}, status=201)

    return JsonResponse({"error": "Invalid request method"}, status=405)

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

            # Check if the user is already enrolled in the course
            if CourseMember.objects.filter(course_id=course, user_id=user).exists():
                return JsonResponse({"error": "User sudah terdaftar di course ini"}, status=400)

            # Check if the course has reached its maximum number of students
            enrolled_students_count = CourseMember.objects.filter(course_id=course).count()
            if enrolled_students_count >= course.max_students:
                return JsonResponse({"error": "Kuota course sudah penuh"}, status=400)

            # Enroll the user in the course
            CourseMember.objects.create(course_id=course, user_id=user)
            return JsonResponse({"message": "User berhasil didaftarkan ke course"}, status=201)

        except Course.DoesNotExist:
            return JsonResponse({"error": "Course tidak ditemukan"}, status=404)
        except User.DoesNotExist:
            return JsonResponse({"error": "User tidak ditemukan"}, status=404)

    return JsonResponse({"error": "Metode permintaan tidak valid"}, status=405)

@csrf_exempt
def batch_enroll_students(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        course_id = data.get('course_id')
        student_ids = data.get('student_ids')

        try:
            course = Course.objects.get(id=course_id)

            for student_id in student_ids:
                student = User.objects.get(id=student_id)

                # Check if the student is already enrolled in the course
                if not CourseMember.objects.filter(course_id=course, user_id=student).exists():
                    # Check if the course has reached its maximum number of students
                    enrolled_students_count = CourseMember.objects.filter(course_id=course).count()
                    if enrolled_students_count < course.max_students:
                        CourseMember.objects.create(course_id=course, user_id=student)
                    else:
                        return JsonResponse({"error": f"Kuota course {course.name} sudah penuh"}, status=400)

            return JsonResponse({"message": "Students berhasil didaftarkan ke course"}, status=201)

        except Course.DoesNotExist:
            return JsonResponse({"error": "Course tidak ditemukan"}, status=404)
        except User.DoesNotExist:
            return JsonResponse({"error": "Salah satu atau lebih user tidak ditemukan"}, status=404)

    return JsonResponse({"error": "Metode permintaan tidak valid"}, status=405)

def list_comments(request, content_id):
    comments = Comment.objects.filter(content_id=content_id, is_approved=True)
    data = serializers.serialize("json", comments)
    return JsonResponse(data, safe=False)

def user_activity_dashboard(request, user_id):
    user = User.objects.get(id=user_id)
    stats = user.get_course_stats()
    return JsonResponse(stats)

def course_analytics(request, course_id):
    course = Course.objects.get(id=course_id)
    stats = course.get_course_stats()
    return JsonResponse(stats)

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