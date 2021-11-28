## @brief Models for the course app.

from django.db import models
from django.contrib.auth.models import User
from instructor.models import Assignment, Course
from django.urls import reverse
from django.utils import timezone

# This class represents the students enrolled in the website.
class Student(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE, default=1)
    name = models.CharField(max_length=100)
    roll_no = models.CharField(max_length=100)
    course_list = models.ManyToManyField(Course,through='Membership',blank=True)

    def __str__(self):
        return self.name

# this class represents the intermediate class between Student and Course
class Membership(models.Model):
    isTA = models.BooleanField(default=False)
    student = models.ForeignKey(Student , on_delete = models.CASCADE)
    course = models.ForeignKey(Course , on_delete = models.CASCADE)
    grade = models.CharField(max_length = 100, blank = True , null = True)
    marks = models.FloatField(default=0, null=True)
    class Meta:
        unique_together = [['student' , 'course']]


# This class represents the messages displayed in the forum.
class Message(models.Model):
    content = models.TextField(max_length=500)
    course = models.ForeignKey(Course,default=1,on_delete=models.CASCADE)
    sender = models.ForeignKey(User,default=1, on_delete=models.CASCADE)
    time = models.CharField(max_length=100)


# This class represents the notifications receieved by the students.
class Notification(models.Model):
    link = models.CharField(max_length=200,blank=True,null=True)
    content = models.TextField(max_length=500)
    course = models.ForeignKey(Course, default=1, on_delete=models.CASCADE)
    time = models.DateTimeField(blank = True, null= True)


# This class represents the resources(lectures/study materials) for a course.
class Resources(models.Model):
    file_resource = models.FileField(default='')
    title = models.CharField(max_length=100)
    course = models.ForeignKey(Course, default=1, on_delete=models.CASCADE)
    post_time = models.DateTimeField(blank = True, null= True)

# This class represents messaging between students
class ChatMessage(models.Model):
     sender = models.ForeignKey(User, related_name="sender", on_delete=models.CASCADE)
     receiver = models.ForeignKey(User, related_name="receiver", on_delete=models.CASCADE)
     msg_content = models.TextField(max_length=500)
     published_at = models.DateTimeField(blank = True, null= True)

     def publish(self):
        self.published_date = timezone.now()
        self.save() 

# model for recording progress for each course for each student
class Progress(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    course = models.ForeignKey(Course,on_delete=models.CASCADE)
    assignments = models.ManyToManyField(Assignment)
    resources = models.ManyToManyField(Resources)
    done = models.IntegerField(default=0)
    total = models.IntegerField(default = 0)
