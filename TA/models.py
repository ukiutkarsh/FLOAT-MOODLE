from django.db import models
from django.contrib.auth.models import User
from course.models import Course

# Create your models here.
# adding TA class

class TeachingAssistant(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE, default=1)
    name = models.CharField(max_length=100)
    information = models.CharField(max_length=1000,default=1)
    course_list = models.ManyToManyField(Course,through='TA_ship')

    def __str__(self):
        return self.name


# this class represents the intermediate class between Student and Course
class TA_ship(models.Model):
    # isTA = models.BooleanField(default=False)
    TA = models.ForeignKey(TeachingAssistant , on_delete = models.CASCADE)
    course = models.ForeignKey(Course , on_delete = models.CASCADE)
    can_add_students = models.BooleanField(default=False,null=True,blank=True)
    can_add_assignments = models.BooleanField(default=False,null=True,blank=True)
    can_add_resources = models.BooleanField(default=False,null=True,blank=True)
    can_notify = models.BooleanField(default=False,null=True,blank=True)
    class Meta:
        unique_together = [['TA' , 'course']]
