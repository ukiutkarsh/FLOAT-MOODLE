## @brief The models registered for the admin site

from django.contrib import admin
from .models import Progress,ChatMessage, Student, Message, Notification, Resources,Membership


admin.site.register(Student)
admin.site.register(Message)
admin.site.register(Notification)
admin.site.register(Resources)
admin.site.register(ChatMessage)
admin.site.register(Progress)
admin.site.register(Membership)
