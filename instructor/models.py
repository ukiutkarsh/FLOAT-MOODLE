## @brief Models for the instructor app.

from django.db import models
from django.contrib.auth.models import User


# This class represents the instructors enrolled in the website
class Instructor(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE, default=1)
    name = models.CharField(max_length=100)
    information = models.CharField(max_length=1000,default=1)

    def __str__(self):
        return self.name


# This class represents the courses.
class Course(models.Model):
    name = models.CharField(max_length=100,default="NAME")
    code = models.CharField(max_length=100,default="CODE")
    course_access_code = models.CharField(max_length=100,default="COURSE_ACCESS_CODE")
    TA_code = models.CharField(max_length=100,default="TA_CODE")
    instructor = models.ForeignKey(Instructor, on_delete=models.CASCADE)
    course_logo = models.FileField(default=1)
    disabled_forum = models.BooleanField(default=False)
    total = models.IntegerField(default=0)

    def __str__(self):
        return self.name


# This class represents the assignments in a course.
class Assignment(models.Model):
    name = models.CharField(max_length=20, default='')
    description = models.CharField(max_length=1000, default='')
    file = models.FileField(default='')
    course = models.ForeignKey(Course,on_delete=models.CASCADE)
    post_time = models.TimeField( auto_now_add=False)
    deadline = models.DateTimeField(blank = True, null= True)
    closed = models.BooleanField(default=False)
    weightage = models.IntegerField(default = 0)



# This class represents the submissions for an assignment.
class Submission(models.Model):
    file_submitted = models.FileField(default='')
    time_submitted = models.CharField(max_length=100)
    user = models.ForeignKey(User,on_delete=models.CASCADE, default=1)
    assignment = models.ForeignKey(Assignment,on_delete=models.CASCADE, default=1)

# This class stores an Image
class ImageObject(models.Model):
    image = models.FileField(default='')

class Feedback(models.Model):
    content = models.TextField(max_length=500)
    submission = models.ForeignKey(Submission,on_delete=models.CASCADE, default=1)
    marks = models.IntegerField(default=-1)


#adding a csv model for grades file
class StudentBulkUpload(models.Model):
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE, default = 1)
    date_uploaded = models.DateTimeField(auto_now=True)
    csv_file = models.FileField(upload_to='media/')

# model for recording progress for each course for each teacher
class ProgressInstructor(models.Model):
    instructor = models.ForeignKey(Instructor, on_delete=models.CASCADE)
    course = models.ForeignKey(Course,on_delete=models.CASCADE)
    assignments = models.ManyToManyField(Assignment)