from ninja import NinjaAPI, UploadedFile, File, Form
from ninja.responses import Response
from lms_core.schema import CourseSchemaOut, CourseMemberOut, CourseSchemaIn
from lms_core.schema import CourseContentMini, CourseContentFull
from lms_core.schema import CourseCommentOut, CourseCommentIn
from lms_core.models import Course, CourseMember, CourseContent, Comment, Category, Announcement  # Tambahkan Announcement
from ninja_simple_jwt.auth.views.api import mobile_auth_router
from ninja_simple_jwt.auth.ninja_auth import HttpJwtAuth
from ninja.pagination import paginate, PageNumberPagination

from django.contrib.auth.models import User

apiv1 = NinjaAPI()
apiv1.add_router("/auth/", mobile_auth_router)
apiAuth = HttpJwtAuth()

@apiv1.get("/hello")
def hello(request):
    return "Hello World"

# - paginate list_courses
@apiv1.get("/courses", response=list[CourseSchemaOut])
@paginate(PageNumberPagination, page_size=10)
def list_courses(request):
    courses = Course.objects.select_related('teacher').all()
    return courses

# - my courses
@apiv1.get("/mycourses", auth=apiAuth, response=list[CourseMemberOut])
def my_courses(request):
    user = User.objects.get(id=request.user.id)
    courses = CourseMember.objects.select_related('user_id', 'course_id').filter(user_id=user)
    return courses

# - create course
@apiv1.post("/courses", auth=apiAuth, response={201:CourseSchemaOut})
def create_course(request, data: Form[CourseSchemaIn], image: UploadedFile = File(None)):
    user = User.objects.get(id=request.user.id)
    category = Category.objects.get(id=data.category_id) if data.category_id else None
    course = Course(
        name=data.name,
        description=data.description,
        price=data.price,
        image=image,
        teacher=user,
        category=category
    )

    if image:
        course.image.save(image.name, image)

    course.save()
    return 201, course

# - update course
@apiv1.post("/courses/{course_id}", auth=apiAuth, response=CourseSchemaOut)
def update_course(request, course_id: int, data: Form[CourseSchemaIn], image: UploadedFile = File(None)):
    if request.user.id != Course.objects.get(id=course_id).teacher.id:
        message = {"error": "Anda tidak diijinkan update course ini"}
        return Response(message, status=401)
    
    course = Course.objects.get(id=course_id)
    category = Category.objects.get(id=data.category_id) if data.category_id else None
    course.name = data.name
    course.description = data.description
    course.price = data.price
    course.category = category
    if image:
        course.image.save(image.name, image)
    course.save()
    return course

# - detail course
@apiv1.get("/courses/{course_id}", response=CourseSchemaOut)
def detail_course(request, course_id: int):
    course = Course.objects.select_related('teacher').get(id=course_id)
    return course

# - list content course
@apiv1.get("/courses/{course_id}/contents", response=list[CourseContentMini])
def list_content_course(request, course_id: int):
    contents = CourseContent.objects.filter(course_id=course_id)
    return contents

# - detail content course
@apiv1.get("/courses/{course_id}/contents/{content_id}", response=CourseContentFull)
def detail_content_course(request, course_id: int, content_id: int):
    content = CourseContent.objects.get(id=content_id)
    return content

# - enroll course
@apiv1.post("/courses/{course_id}/enroll", auth=apiAuth, response=CourseMemberOut)
def enroll_course(request, course_id: int):
    user = User.objects.get(id=request.user.id)
    course = Course.objects.get(id=course_id)
    course_member = CourseMember(course_id=course, user_id=user, roles="std")
    course_member.save()
    return course_member

# - list content comment
@apiv1.get("/contents/{content_id}/comments", auth=apiAuth, response=list[CourseCommentOut])
def list_content_comment(request, content_id: int):
    comments = Comment.objects.filter(content_id=content_id, is_approved=True)
    return comments

# - create content comment
@apiv1.post("/contents/{content_id}/comments", auth=apiAuth, response={201: CourseCommentOut})
def create_content_comment(request, content_id: int, data: CourseCommentIn):
    user = User.objects.get(id=request.user.id)
    content = CourseContent.objects.get(id=content_id)

    if not content.course_id.is_member(user):
        message =  {"error": "You are not authorized to create comment in this content"}
        return Response(message, status=401)
    
    member = CourseMember.objects.get(course_id=content.course_id, user_id=user)
    
    comment = Comment(
        content_id=content,
        member_id=member,
        comment=data.comment
    )
    comment.save()
    return 201, comment

# - delete content comment
@apiv1.delete("/comments/{comment_id}", auth=apiAuth)
def delete_comment(request, comment_id: int):
    comment = Comment.objects.get(id=comment_id)
    if comment.member_id.user_id.id != request.user.id:
        return {"error": "You are not authorized to delete this comment"}
    comment.delete()
    return {"message": "Comment deleted"}

# - add category
@apiv1.post("/categories", auth=apiAuth, response={201: dict})
def add_category(request, data: dict):
    user = User.objects.get(id=request.user.id)
    category = Category.objects.create(name=data['name'], created_by=user)
    return 201, {"message": "Kategori berhasil dibuat"}

# - show categories
@apiv1.get("/categories", response=list[dict])
def show_categories(request):
    categories = Category.objects.all()
    return [{"id": category.id, "name": category.name} for category in categories]

# - delete category
@apiv1.delete("/categories/{category_id}", auth=apiAuth, response={200: dict})
def delete_category(request, category_id: int):
    user = User.objects.get(id=request.user.id)
    category = Category.objects.get(id=category_id)
    if category.created_by != user:
        return Response({"error": "Hanya user yang membuat kategori yang dapat menghapusnya"}, status=403)
    category.delete()
    return {"message": "Kategori berhasil dihapus"}

# - create announcement
@apiv1.post("/announcements", auth=apiAuth, response={201: dict})
def create_announcement(request, data: dict):
    user = User.objects.get(id=request.user.id)
    course = Course.objects.get(id=data['course_id'])
    if course.teacher != user:
        return Response({"error": "Hanya teacher yang dapat membuat pengumuman"}, status=403)
    announcement = Announcement.objects.create(
        course=course,
        title=data['title'],
        content=data['content'],
        release_date=data['release_date']
    )
    return 201, {"message": "Pengumuman berhasil dibuat"}

# - show announcements
@apiv1.get("/announcements/{course_id}", response=list[dict])
def show_announcements(request, course_id: int):
    course = Course.objects.get(id=course_id)
    announcements = Announcement.objects.filter(course=course, release_date__lte=timezone.now())
    return [{"id": announcement.id, "title": announcement.title, "content": announcement.content, "release_date": announcement.release_date} for announcement in announcements]

# - edit announcement
@apiv1.post("/announcements/{announcement_id}", auth=apiAuth, response={200: dict})
def edit_announcement(request, announcement_id: int, data: dict):
    user = User.objects.get(id=request.user.id)
    announcement = Announcement.objects.get(id=announcement_id)
    if announcement.course.teacher != user:
        return Response({"error": "Hanya teacher yang dapat mengedit pengumuman"}, status=403)
    announcement.title = data['title']
    announcement.content = data['content']
    announcement.release_date = data['release_date']
    announcement.save()
    return {"message": "Pengumuman berhasil diubah"}

# - delete announcement
@apiv1.delete("/announcements/{announcement_id}", auth=apiAuth, response={200: dict})
def delete_announcement(request, announcement_id: int):
    user = User.objects.get(id=request.user.id)
    announcement = Announcement.objects.get(id=announcement_id)
    if announcement.course.teacher != user:
        return Response({"error": "Hanya teacher yang dapat menghapus pengumuman"}, status=403)
    announcement.delete()
    return {"message": "Pengumuman berhasil dihapus"}