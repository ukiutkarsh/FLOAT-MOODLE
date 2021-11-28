## @brief The models registered for the admin site

from django.contrib import admin
from .models import StudentBulkUpload,Instructor, Course, Assignment, Submission,Feedback


admin.site.register(Instructor)
admin.site.register(Course)
admin.site.register(Assignment)
admin.site.register(Submission)
admin.site.register(Feedback)
admin.site.register(StudentBulkUpload)
