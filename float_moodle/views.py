## @brief Views for the course app.

from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect

from instructor.views import instructor_detail
from .forms import UserRegistration, StudentRegistration, InstructorForm,CreateCourse,TAform
from course.models import Progress, Student, User
from django.contrib.auth.forms import PasswordResetForm
from instructor.models import Instructor, ProgressInstructor
from django.db.models.query_utils import Q
from django.core.mail import BadHeaderError
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.template.loader import render_to_string
from django.db.models.query_utils import Q
from django.utils.http import urlsafe_base64_encode
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes
from TA.models import TeachingAssistant
from instructor.functions import send_email,email_from
import threading

## @brief view for the login page of the website.
#
# This view is called by /login url.\n
# It returns the login page for the students and instructors to login.
def login_user(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            try:
                student = Student.objects.get(user=request.user)
                return redirect('course:index')
            except:
                try:
                    ta = TeachingAssistant.objects.get(user=request.user)
                    return redirect('TA:TA_index')
                except:
                    return redirect('instructor:instructor_index')
        else:
            return render(request, 'login.html', {'error_message': 'Invalid login credentials'})
    return render(request, 'login.html')


# view for the registration page for students to register themselves.
# This view is called by /register_user url.\n
# It returns the form for students to register themselves.\n
# The students can choose a usename and password and fill out their details and select the courses they wish to enroll in.
def register_user(request):
    user_form = UserRegistration(request.POST or None)
    student_form = StudentRegistration(request.POST or None)

    if user_form.is_valid() and student_form.is_valid():
        user = user_form.save(commit=False)
        username = user_form.cleaned_data['username']
        password = user_form.cleaned_data['password']
        email = user_form.cleaned_data['email']
        user.set_password(password)
        user.save()

        student = student_form.save(commit=False)
        student.user = User.objects.get(id=user.id)
        student.save()
        student_form.save_m2m() # saves the many to many field relation (between the course and student model) entered in the form while selecting the courses
        #make progress model for each course
        courses=student_form.cleaned_data['course_list']
        for c in courses:
            progress=Progress()
            progress.student=student
            progress.course=c
            progress.save()            
        return login_user(request)

    return render(request,'register_user.html', {'user_form': user_form, 'student_form': student_form})

# view for registration page of instructor

def register_instructor(request):
    user_form = UserRegistration(request.POST or None)
    instructor_form = InstructorForm(request.POST or None)

    if user_form.is_valid() and instructor_form.is_valid():
        user = user_form.save(commit=False)
        username = user_form.cleaned_data['username']
        password = user_form.cleaned_data['password']
        user.set_password(password)
        user.save()

        instructor = instructor_form.save(commit=False)
        instructor.user = User.objects.get(id=user.id)
        instructor.save()
        # instructor_form.save_m2m() # saves the many to many field relation (between the course and student model) entered in the form while selecting the courses

        return login_user(request)

    return render(request,'register_instructor.html', {'user_form': user_form, 'instructor_form': instructor_form})

# view for the registration page for TAs to register themselves.
# This view is called by /register_TA url.\n
# It returns the form for TAs to register themselves.\n
# The students can choose a usename and password and fill out their details.
def register_TA(request):
    user_form = UserRegistration(request.POST or None)
    TA_form = TAform(request.POST or None)

    if user_form.is_valid() and TA_form.is_valid():
        user = user_form.save(commit=False)
        username = user_form.cleaned_data['username']
        password = user_form.cleaned_data['password']
        email = user_form.cleaned_data['email']
        user.set_password(password)
        user.save()

        TA = TA_form.save(commit=False)
        TA.user = User.objects.get(id=user.id)
        TA.save()
        # student_form.save_m2m() # saves the many to many field relation (between the course and student model) entered in the form while selecting the courses
        #make progress model for each course      
        return login_user(request)

    return render(request,'register_TA.html', {'user_form': user_form, 'TA_form': TA_form})

## @brief view for the logout page.
#
# This view is called by /logout_user url.\n
# It returns the webpage displayed when the user log outs of the website which is same as the login page.
def logout_user(request):
    logout(request)
    return render(request, 'login.html')

def divide(request):
    return render(request, 'divide.html')

def add_course(request):
    course_form = CreateCourse(request.POST, request.FILES)

    if course_form.is_valid():
        course = course_form.save(commit=False)
        course.instructor = Instructor.objects.get(user=request.user)
        course.save()
        #add progress for new course for instructor
        instructor = Instructor.objects.get(user = request.user)
        p = ProgressInstructor()
        p.course = course
        p.instructor=instructor
        p.save()
        return redirect('instructor:instructor_index')
        
    return render(request, 'create_course.html', {'course_form': course_form})


def password_reset_request(request):
    if request.method == "POST":
        password_reset_form = PasswordResetForm(request.POST)
        if password_reset_form.is_valid():
            data = password_reset_form.cleaned_data['email']
            associated_users = User.objects.filter(Q(email=data))
            if associated_users.exists():
                user = associated_users.first()
                recipient_list = [user.email]
               
                subject = "Password Reset Requested"
                email_template_name = "password_reset_email.txt"
                c = {
                "email":user.email,
                'domain':'127.0.0.1:8000',
                'site_name': 'Website',
                "uid": urlsafe_base64_encode(force_bytes(user.pk)),
                "user": user,
                'token': default_token_generator.make_token(user),
                'protocol': 'http',
                }
                email_text = render_to_string(email_template_name, c)
                sender = email_from()
                print(email_text)
                print(sender)

                thread = threading.Thread(target=send_email,args=(subject, email_text, sender, recipient_list, None,))
                thread.start()
                return redirect ("/password_reset/done/")
    password_reset_form = PasswordResetForm()
    return render(request=request, template_name="password_reset.html", context={"password_reset_form":password_reset_form})
