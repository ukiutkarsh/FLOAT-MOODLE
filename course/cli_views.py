from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny
from course.models import Resources, Student
from django.contrib.auth import login, models, update_session_auth_hash
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from course.models import Progress
from instructor.models import Assignment, Course, Instructor

def rest_login(request):
    data = {}
    # reqBody = json.loads(request.body)
    print(request)
    username = request.data.get("username")
    password = request.data.get('password')
    try:
        Account = User.objects.get(username=username)
    except BaseException as e:
        raise ValidationError({"400": f'{str(e)}'})
    token = Token.objects.get_or_create(user=Account)[0].key
    print(token)
    if not Account.check_password(password):
        raise ValidationError({"message": "Incorrect Login credentials"})
    if Account:
        if Account.is_active:
            login(request, Account)
            request.session.save()
            return True
        else:
            return False

    else:
        return False

@api_view(["POST"])
@permission_classes([AllowAny]) 
def cli_courses(request):
    if rest_login(request):
        # try:
            x = request.data.get("roll_num")
            student = Student.objects.filter(roll_no=x).first()
            print(student.roll_no)
            print(student)
            # print(student.user.username)
            course_names = []
            instructor_names = []
            for i in student.course_list.all():
                course_names.append(i.name)
                instructor_names.append(i.instructor.name)
            response = {'courses' : course_names,'instructors':instructor_names}
            print(response)
            return Response(response)
        # except:
        #     print("failed")
        #     response = {'courses':[]}
        #     return Response(response)
    else:
        raise ValidationError({"400": f'Some Problem'})


@api_view(["POST"])
@permission_classes([AllowAny]) 
def cli_pending(request):
    if rest_login(request):
        # try:
            x = request.data.get("roll_num")
            student = Student.objects.filter(roll_no=x).first()
            print(student)
            course_names = []
            pending_assignments_list = []
            pending_resources_list=[]
            for i in student.course_list.all():
                assignments_list = ''
                resources_list =''
                course_names.append(i.name)
                assignments = Assignment.objects.filter(course = i)
                resources = Resources.objects.filter(course=i)
                progress = Progress.objects.get(course = i, student = student)
                for a in assignments:
                    if not a in progress.assignments.all():
                        assignments_list += (str(a.name)+" Due At: " + str(a.deadline)[:-9])
                pending_assignments_list.append(assignments_list)
                for r in resources:
                    if not r in progress.resources.all():
                        resources_list+=(str(r.title))
                pending_resources_list.append(resources_list)
            response = {'courses' : course_names,'pending_assignments_list':pending_assignments_list,'pending_resources_list':pending_resources_list}
            print(response)
            return Response(response)

@api_view(["POST"])
@permission_classes([AllowAny]) 
def cli_student_list(request):
    if rest_login(request):
        # try:
            print('here')
            x = request.data.get("name")
            # print(x)
            instructor = Instructor.objects.get(name=x)
            print(instructor.name)
            courses = Course.objects.filter(instructor=instructor)
            print(courses)
            course_list = []
            student_list = []
            for i in courses:
                students = Student.objects.filter(course_list__id= i.id)

                student_list.append(students)
            response = {'courses' : course_list,'student_list':student_list}
            print(response)
            return Response(response)
        # except:
        #     print("failed")
        #     response = {'courses':[]}
        #     return Response(response)
    else:
        raise ValidationError({"400": f'Some Problem'})