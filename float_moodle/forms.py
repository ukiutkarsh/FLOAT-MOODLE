## @brief Forms for the course app.

from django import forms
from django.contrib.auth.models import User
from course.models import Student
from instructor.models import Course, Instructor
from TA.models import TeachingAssistant

# This class represents the form to register a user.
class UserRegistration(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    email = forms.EmailField()
    class Meta:
        model = User
        fields = ['username', 'password','email']


# This class represents the form to register a student.
class StudentRegistration(forms.ModelForm):

    class Meta:
        model = Student
        fields = ['name', 'roll_no', 'course_list']

class InstructorForm(forms.ModelForm):
    class Meta:
        model = Instructor
        fields = ['name', 'information']

class CreateCourse(forms.ModelForm):    
    class Meta:
        model = Course
        # fields = ['name', 'code','course_logo']
        fields = ['name', 'code','course_access_code','TA_code', 'course_logo']

class TAform(forms.ModelForm):
    class Meta:
        model = TeachingAssistant
        fields = ['name', 'information']